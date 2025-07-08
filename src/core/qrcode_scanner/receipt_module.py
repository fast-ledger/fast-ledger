import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from pyzbar.pyzbar import decode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib
import chardet #檢查編碼
#pip install playsound
#pip install watchdog

folder_path = Path("C:/Users/user/AI2025/Receipt")



# 🔽 載入原 receipt 處理邏輯
def process_new_image(image_path):
    #image_path = file_path
    print(f"\n📥 開始處理：{image_path}")
    if not os.path.exists(image_path):
        print("⚠️ 圖片路徑無效")
        return
    
    try:
        img_original = cv2.imread(image_path)
        if img_original is None:
            print(f"⚠️ 無法讀取圖片：{image_path}")
            return

        img = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)

        def putText(img,x, y, text, color=(0, 255, 0)):
            #global img_original # 在彩色圖片上繪製文字
            # 使用支持中文的字体
            fontpath = r'C:\Users\user\AI2025\fonts\DejaVuSans-Bold.ttf'  # 默認字體
            try:
                fontpath = r'C:\Users\user\AI2025\fonts\NotoSansTC-VariableFont_wght.ttf'  # 如果上傳了中文字體
            except:
                pass

            # 嘗試加載字體並設置大小
            try:
                font = ImageFont.truetype(fontpath, 20)
            except:
                font = ImageFont.load_default()

            # 轉換為 PIL 圖像進行繪製
            imgPil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # 轉換為 RGB 格式
            draw = ImageDraw.Draw(imgPil)
            draw.text((x, y), text, fill=color, font=font)  # 繪製文本

            # 轉回 OpenCV 圖像
            img = cv2.cvtColor(np.array(imgPil), cv2.COLOR_RGB2BGR)

            if img is None:
                print(f"⚠️ 無法讀取並標示圖片：{image_path}")
                return

        def boxSize(arr):
            box_roll = np.rollaxis(arr, 1, 0)
            xmax = int(np.amax(box_roll[0]))
            xmin = int(np.amin(box_roll[0]))
            ymax = int(np.amax(box_roll[1]))
            ymin = int(np.amin(box_roll[1]))
            return (xmin, ymin, xmax, ymax)
        
        # 全形轉半形函數 2025/7/7
        def fullwidth_to_halfwidth(s):
            result = ''
            for char in s:
                code = ord(char)
                # 全形空格轉半形空格
                if code == 0x3000:
                    code = 0x0020
                # 其他全形字符轉換（全形範圍：FF01-FF5E）
                elif 0xFF01 <= code <= 0xFF5E:
                    code -= 0xFEE0
                result += chr(code)
            return result
        
        #中文編碼方式() 2025/7/7 13:27
        def extract_encoding_flag(product_info_substring):
            colon_count = 0
            for idx, char in enumerate(product_info_substring):
                if char == ":":
                    colon_count += 1
                    if colon_count == 3 and idx + 1 < len(product_info_substring):
                        return product_info_substring[idx + 1]
            return None  # 沒找到時

        def decode_by_flag(decoded_objects, flag):
            import base64

            try:
                if flag == '0':  # big5
                    encoding = 'big5'
                    content_obj_0 = decoded_objects[0].data.decode('big5')
                    if len(decoded_objects) > 1:
                        content_obj_1 = decoded_objects[1].data.decode('big5')
                    else:
                        content_obj_1 = ''
                elif flag == '1':  # UTF-8
                    encoding = 'utf-8'
                    content_obj_0 = decoded_objects[0].data.decode('utf-8')
                    if len(decoded_objects) > 1:
                        content_obj_1 = decoded_objects[1].data.decode('utf-8')
                    else:
                        content_obj_1 = ''
                elif flag == '2':  # Base64
                    encoding = 'base64'
                    merged_bytes = b''.join([obj.data for obj in decoded_objects])
                    content_obj_0 = base64.b64decode(merged_bytes).decode('utf-8')
                    if len(decoded_objects) > 1:
                        content_obj_1 = decoded_objects[1].data.decode('utf-8')
                    else:
                        content_obj_1 = ''
                else:  # fallback
                    encoding = 'utf-8' #2025/7/7 16:47
                    content_obj_0 = decoded_objects[0].data.decode('utf-8', errors='replace')
                    content_obj_1 = decoded_objects[1].data.decode('utf-8', errors='replace') if len(decoded_objects) > 1 else ''
            except Exception as e:
                print(f"❌ 解碼錯誤 ({flag}): {e}")
                return decoded_objects[0].data.decode('utf-8', errors='replace')  # fallback

            # 避免錯亂 QR Code 順序
            if content_obj_0.startswith("**"):
                content_obj_0, content_obj_1 = content_obj_1, content_obj_0

            return encoding,content_obj_0 + content_obj_1 #2025/7/7 17:00



        # 優先使用 OpenCV 的 QRCode 偵測器
        qrcode = cv2.QRCodeDetector()

        # 應用高斯模糊以提高偵測率 (暫時不使用)
        #img_blur = cv2.GaussianBlur(binary, (5, 5), 0)

        # 在灰度圖片上執行解碼
        ok, data, bbox, rectified = qrcode.detectAndDecodeMulti(img) # *** 修改這裡 ***

        # 偵錯：確認是否成功讀取到 QR Code 內容
        if ok:
            print("OpenCV成功讀取QR Code 內容：")
            for i in range(len(data)):
                print(f"內容: {data[i]}")  # 打印 QR Code 內容
                print(f"坐標: {bbox[i]}")  # 打印 QR Code 邊框坐標

                text = data[i]  # QRCode 內容
                box = boxSize(bbox[i])  # 獲取 QRCode 邊框坐標
                # 在原始彩色圖片上繪製矩形框
                cv2.rectangle(img_original, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 5)

                # 調整文字位置，避免重疊
                # 使用 img_original 放置文字
                putText(img_original,box[0] + 10, box[3] + 25, text, color=(0, 255, 0))  # 07041322在圖片上寫出文本，增加偏移量

            
            #嘗試使用不同的 QR Code 偵測庫
            #pyzbar 是另一個常用的 Python 庫，專門用於讀取條碼和 QR Code。它通常比 OpenCV 的內建偵測器更為穩定和易用。
            
        else:
            print("⚠️ OpenCV 無法解出 QR Code，使用 pyzbar 備援...")

            # 讀取圖片
            try:
                
                # 使用 pyzbar 偵測和解碼 QR Code
                decoded_objects = decode(Image.open(image_path))
                decoded_objects_old = decode(image_path)
                
                # 檢查是否有偵測到 QR Code
                if decoded_objects:
                    print("pyzbar成功讀取到 QR Code 內容：")
                    for obj in decoded_objects:
                        # 解碼後的資料通常是 bytes，需要轉換為字串 data_bytes = obj.data
                        qrcode_data = obj.data.decode('utf-8')
                        qrcode_data = fullwidth_to_halfwidth(qrcode_data) #2025/7/7
                        print(f"內容: {qrcode_data}")
                        print(f"類型: {obj.type}")
                        print(f"位置: {obj.rect}")
                        


                else:
                    print("未能讀取到 QR Code 內容，請檢查圖片或 QR Code 是否清晰。")

            except FileNotFoundError:
                print(f"錯誤：找不到圖片檔案 {image_path}")
            except Exception as e:
                print(f"發生錯誤：{e}")


        if decoded_objects:
            total_product_amount = 0
            product_list = [] # 確保 product_list 在這裡被初始化

        # 使用 matplotlib 顯示結果
        # 顯示修改後的原始彩色圖片
            #matplotlib.use('Agg')
            #plt.imshow(cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB))
            #plt.axis('off')  # 關閉座標軸
            #plt.savefig(f"output_image_{i+1}.png") #("output_image" + str(i+1) + ".png")

            qrcode_data_1 = None
            qrcode_data_2 = None
        
        if len(decoded_objects) > 0:
            print(f"偵測到的 QR Code 數量: {len(decoded_objects)}")
            # 獲取第一個 decoded object 的內容
            content_obj_0 = decoded_objects[0].data.decode('utf-8')
            print(f"第一個 QR Code 內容 (content_obj_0): {content_obj_0}")

            if len(decoded_objects) >= 2:
                # 獲取第二個 decoded object 的內容
                content_obj_1 = decoded_objects[1].data.decode('utf-8')
                print(f"第二個 QR Code 內容 (content_obj_1): {content_obj_1}")

                # 判斷哪個是第一個 QR Code 的內容
                # 修改這裡的判斷邏輯：非 ** 開頭才是第一個 QR Code
                if not content_obj_0.startswith("**"):
                    qrcode_data_1 = content_obj_0
                    qrcode_data_2 = content_obj_1
                    qrcode_all  = qrcode_data_1 + qrcode_data_2
                else:
                    qrcode_data_1 = content_obj_1
                    qrcode_data_2 = content_obj_0
                    qrcode_all  = qrcode_data_1 + qrcode_data_2
            else:
                # 只有一個 QR Code 的情況
                qrcode_data_1 = content_obj_0
                qrcode_all = qrcode_data_1
            print(f"qrcode_all 的內容: {qrcode_all}") # 查看最終的 qrcode_all

        else:
            print("沒有偵測到 QR Code")

#////重新解析內容，亂碼修正////
        product_info_substring = qrcode_all[88:]
        parts = qrcode_all.split(':')
        encoding_flag = extract_encoding_flag(product_info_substring)
        decoded_text = ""

        if len(parts) > 3:
            #encoding_flag = parts[4]
            print(f"第三個冒號後的數字(編碼標記): {encoding_flag}")

            if decoded_objects:
                qrcode_all = decode_by_flag(decoded_objects, encoding_flag)
                encoding, qrcode_all = decode_by_flag(decoded_objects, encoding_flag) #2025/7/7 17:11 test

                print(f"📦 解碼後內容：\n{qrcode_all}")
            else:
                print("⚠️ 無法解碼 QR Code")
                return
            
        else:
            print("⚠️ 字串格式錯誤，冒號數量不足")
            decoded_text = qrcode_all

        #print(f"最終解碼結果:\n{decoded_text}")
        product_info_substring = qrcode_all[88:]

        # 解析 QR Code 的內容
        if qrcode_all:
            # 提取發票號碼 (字串1~10)
            invoice_number = qrcode_all[0:10]

            # 提取發票開立日 (字串11~17) - 注意索引是從0開始，所以是10~16
            invoice_date = qrcode_all[10:17] # 格式可能是YYYMMDD

            # 提取銷售額 (字串22~29) - 注意索引是從0開始，所以是21~28
            sales_amount_hex = qrcode_all[21:29]
            # 將16進制轉換為10進制
            try:
                sales_amount_decimal = int(sales_amount_hex, 16)
            except ValueError:
                sales_amount_decimal = "轉換錯誤，非法的16進制字串"

            # 提取總計額 (字串30~37) - 注意索引是從0開始，所以是29~36
            total_amount_hex = qrcode_all[29:37]
            # 將16進制轉換為10進制
            try:
                total_amount_decimal = int(total_amount_hex, 16)
            except ValueError:
                total_amount_decimal = "轉換錯誤，非法的16進制字串"

            # 提取賣方統編 (字串46~53) - 注意索引是從0開始，所以是45~52
            seller_id = qrcode_all[45:53]

            # 提取第一個 QR Code 的商品資訊 (從第 88 位後第四個冒號後取字串)
            #product_info_substring = qrcode_all[88:] 2025/7/7 11:36
            product_info_raw_1 = "" # 初始化
            colon_count = 0
            start_index = -1

            for i in range(len(product_info_substring)):
                if product_info_substring[i] == ':':
                    colon_count += 1
                    if colon_count == 4:
                        start_index = i + 1 # 從第四個冒號的下一個字元開始
                        break

            if start_index != -1:
                product_info_raw_1 = product_info_substring[start_index:]

            product_info_raw_1= product_info_raw_1.replace("**", "")

            print(product_info_raw_1)
            print("----------------------------------------------------")
            # *** DEBUG END ***


        if product_info_raw_1:
            parts = product_info_raw_1.split(':')
            # 直接從parts的開頭開始解析，每次取3個元素 (品名、數量、單價)
            for i in range(0, len  (parts), 3):
                if i + 2 < len(parts):
                    product_name = parts[i]
                    quantity_str = parts[i+1]
                    unit_price_str = parts[i+2]
                    try:
                        quantity = int(quantity_str)
                        unit_price = int(unit_price_str)
                        item_total = quantity * unit_price
                        total_product_amount += item_total # 累計商品總金額
                        #product_list.append(f"商品品項: {product_name}, 數量: {quantity}, 單價: {unit_price}, 小計: {item_total}")
                        product_list.append({
                                                '商品品項': product_name,
                                                '數量': quantity,
                                                '單價': unit_price,
                                                '小計': item_total
                                            })
                    except ValueError:
                        #product_list.append(f"商品品項: {product_name}, 數量: {quantity_str}, 單價: {unit_price_str}, 小計: 解析錯誤")
                        product_list.append({
                                                '商品品項': product_name,
                                                '數量': quantity_str,
                                                '單價': unit_price_str,
                                                '小計': "解析錯誤"
                                            })

        def min_to_g_year(min_date):
            min_date = int(min_date)
            min_year = min_date // 10000
            month = (min_date % 10000) // 100
            day = min_date % 100
            g_year = min_year + 1911
            return datetime(g_year, month, day).strftime('%Y/%m/%d')

        g_date_str = min_to_g_year(invoice_date)

        print("\n--- 發票資訊 ---")
        print(f"發票號碼: {invoice_number}")
        print(f"發票開立日: {g_date_str}")
        print(f"銷售額 (10進制): {sales_amount_decimal}")
        print(f"總計額 (10進制): {total_amount_decimal}")
        print(f"賣方統編: {seller_id}")

        for p in product_list:
            print(p)
        print(f"商品總金額: {total_product_amount}")


        encoding, decoded_content = decode_by_flag(decoded_objects, encoding_flag) #2025/7/7 17:07
        with open("invoice_output.txt", "a", encoding=encoding) as f: #2025/7/7 16:32
            f.write("\n--- 發票資訊 ---\n")
            f.write(f"發票號碼: {invoice_number}\n")
            f.write(f"發票開立日: {g_date_str}\n")
            f.write(f"銷售額 (10進制): {sales_amount_decimal}\n")
            f.write(f"總計額 (10進制): {total_amount_decimal}\n")
            f.write(f"賣方統編: {seller_id}\n")
            for product in product_list:
                f.write(f"{product}\n")
            f.write(f"商品總金額: {total_product_amount}\n")

        with open("invoice_data.csv", "a", newline="", encoding=encoding) as csvfile: #2025/7/7 16:33
            writer = csv.writer(csvfile)
            if os.stat("invoice_data.csv").st_size == 0:
                writer.writerow(["發票號碼", "日期", "統編", "商品", "數量", "單價", "小計", "總金額"])
            for p in product_list:
                writer.writerow([invoice_number, g_date_str, seller_id, p['商品品項'], p['數量'], p['單價'], p['小計'], total_product_amount])

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("python-gogglesheet-97f9ad6db89e.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("測試帳本-API").sheet1

        def find_next_empty_row(col_index):
            return len(sheet.col_values(col_index)) + 1

        row_f = find_next_empty_row(6)
        for i, p in enumerate(product_list):
            sheet.update(values=[[seller_id, g_date_str]], range_name=f"F{row_f+i}:G{row_f+i}")
            #sheet.update(range_name=f"F{row_f+i}:G{row_f+i}", values=[[seller_id, g_date_str]])

        row_h = find_next_empty_row(8)
        for i, p in enumerate(product_list):
            h_val = f"{p['商品品項']} x{p['數量']}"
            i_val = p['數量']
            j_val = p['小計']
            sheet.update(range_name=f"H{row_h+i}:J{row_h+i}",values=[[h_val, i_val, j_val]])

        print("✅ 已寫入 Google Sheet 和 CSV / TXT")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

def wait_for_file_stable(file_path, wait_seconds=2):
    prev_size = -1
    stable_count = 0
    while stable_count < 3:
        try:
            curr_size = os.path.getsize(file_path)
            if curr_size == prev_size:
                stable_count += 1
            else:
                stable_count = 0
                prev_size = curr_size
        except FileNotFoundError:
            stable_count = 0
        time.sleep(wait_seconds / 3)



# 🔍 取得最新圖檔並處理
def process_latest_image(folder_path):
    print(f"收到的圖片路徑：{folder_path}")
    print(f"檔案是否存在：{os.path.exists(newest_image)}")
    folder = Path(folder_path)
    img_ext = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

    image_files = [f for f in folder.iterdir() if f.suffix.lower() in img_ext]
    image_files_sorted = sorted(image_files, key=lambda f: f.stat().st_mtime)

    if image_files_sorted:
        newest_image = image_files_sorted[-1]
        print(f"🆕 最新圖檔：{newest_image.name}")
        process_new_image(str(newest_image))
    else:
        print("⚠️ 資料夾內沒有圖檔")


# 📂 自動監控資料夾新增圖檔
class ImageCreatedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}:
                print(f"📸 偵測到新圖檔：{file_path.name}")
                time.sleep(0.5)
                process_new_image(str(file_path))

def start_watch_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        folder.mkdir(parents=True)

    event_handler = ImageCreatedHandler()
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=False)
    observer.start()

    print(f"🕵️ 開始監控資料夾：{folder.resolve()}，等待新圖檔...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watch_folder(folder_path)
    image_path = "C:\\Users\\user\\AI2025\\Receipt\\Receipt_1.jpg"
    process_new_image(image_path)