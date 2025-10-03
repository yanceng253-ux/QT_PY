# 1. 导入所需库
import cv2  # 调用摄像头、处理图像
import requests  # 发送API请求
import base64  # 图片转Base64编码
import json  # 解析API返回的JSON结果

# 2. 配置百度智能云密钥（替换为你的密钥！）
APP_ID = "7100633"
API_KEY = "dYAao4ghu72m72S1YBBgv7Be"
SECRET_KEY = "DdlJDLK7nF2IxR3Tx9wUK1CDa7YjFkM8"

# 3. 第一步：获取百度API的临时凭证（Access Token，有效期30天）
def get_baidu_access_token():
    # 百度获取Token的接口地址
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    try:
        # 发送请求获取Token
        response = requests.get(token_url)
        token_data = response.json()
        # 提取Token（若失败，会抛出异常提示错误）
        if "access_token" in token_data:
            return token_data["access_token"]
        else:
            raise Exception(f"获取Token失败：{token_data['error_description']}")
    except Exception as e:
        print(f"Token获取出错：{str(e)}")
        return None

# 4. 第二步：调用百度智能云车牌识别API，解析车牌号
def recognize_plate(access_token, image_base64):
    # 百度车牌识别API接口地址
    plate_api_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/license_plate?access_token={access_token}"
    # 请求参数：传入Base64编码的图像
    params = {"image": image_base64}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        # 发送POST请求调用API
        response = requests.post(plate_api_url, data=params, headers=headers)
        print("API返回原始结果：", response.text)  # 保留打印，方便后续排查
        result = response.json()
        
        # 关键修改：判断是否识别到车牌（依赖words_result和number字段）
        if "words_result" in result and "number" in result["words_result"]:
            plate_info = result["words_result"]
            plate_number = plate_info["number"]  # 核心：车牌号
            plate_color = plate_info.get("color", "未知颜色")  # 用get避免字段缺失
            # 提取置信度（可选，判断识别结果可靠性）
            probability = plate_info.get("probability", [0.0])[0]  
            
            print(f"\n【识别成功！】")
            print(f"车牌号：{plate_number}")
            print(f"车牌颜色：{plate_color}")
            print(f"识别置信度：{probability:.6f}")  # 显示可信度（0-1，越近1越准）
            return plate_number  # 返回车牌号
        else:
            # 未识别到车牌或字段缺失
            error_msg = result.get("error_msg", "未识别到车牌，请调整摄像头角度/光线")
            print(f"【识别失败】：{error_msg}")
            return None
    except Exception as e:
        print(f"API调用出错（代码逻辑/网络问题）：{str(e)}")
        return None

# 5. 第三步：调用本地摄像头，抓拍车牌图像
def capture_plate_with_camera():
    # 打开本地摄像头（0表示默认摄像头，若外接摄像头可尝试1、2等）
    cap = cv2.VideoCapture(0)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头，请检查摄像头是否连接正常！")
        return None
    
    print("\n=== 摄像头已启动 ===")
    print("提示：请将车牌对准摄像头，按 's' 键抓拍，按 'q' 键退出")
    
    while True:
        # 实时读取摄像头画面（ret：是否读取成功，frame：画面帧）
        ret, frame = cap.read()
        if not ret:
            print("无法获取摄像头画面，退出程序")
            break
        
        # 在画面上显示操作提示文字
        cv2.putText(frame, "Press 's' to capture, 'q' to quit", 
                    (10, 30),  # 文字位置（左上角）
                    cv2.FONT_HERSHEY_SIMPLEX,  # 字体
                    0.8,  # 字体大小
                    (0, 255, 0),  # 文字颜色（绿色）
                    2)  # 文字粗细
        
        # 显示实时画面（窗口标题："Camera - Plate Recognition"）
        cv2.imshow("Camera - Plate Recognition", frame)
        
        # 等待键盘输入（1ms延迟，避免占用过高CPU）
        key = cv2.waitKey(1) & 0xFF
        
        # 按 's' 键：抓拍当前画面并保存
        if key == ord('s'):
            # 保存抓拍的图片到本地（路径：当前文件夹下的 "captured_plate.jpg"）
            captured_path = "captured_plate.jpg"
            cv2.imwrite(captured_path, frame)
            print(f"\n已抓拍图片，保存路径：{captured_path}")
            
            # 将抓拍的图片转成Base64编码（百度API要求格式）
            with open(captured_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")
            
            # 关闭摄像头和窗口（抓拍后退出循环）
            cap.release()
            cv2.destroyAllWindows()
            return image_base64  # 返回Base64编码的图片
        
        # 按 'q' 键：退出程序
        elif key == ord('q'):
            print("\n用户退出程序")
            cap.release()
            cv2.destroyAllWindows()
            return None

# 6. 主函数：串联所有步骤（摄像头抓拍→API识别→返回车牌号）
def main():
    # 步骤1：获取百度API Token
    access_token = get_baidu_access_token()
    if not access_token:
        print("无法获取API凭证，程序终止")
        return
    
    # 步骤2：调用摄像头抓拍车牌，获取Base64图片
    image_base64 = capture_plate_with_camera()
    if not image_base64:
        print("未获取到有效图片，程序终止")
        return
    
    # 步骤3：调用百度API识别车牌，返回车牌号
    plate_number = recognize_plate(access_token, image_base64)
    if plate_number:
        print(f"\n最终识别结果：车牌号 = {plate_number}")
    else:
        print("\n未成功识别车牌号")

# 7. 运行主函数（程序入口）
if __name__ == "__main__":
    main()
