import time
import pandas as pd
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_browser():
    """
    设置浏览器
    """
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def open_website(driver):
    """
    打开网站并等待用户手动设置
    """
    driver.get("https://www.pkulaw.com/advanced/law/chl")
    print("\n请在浏览器中设置您需要的搜索条件并点击搜索，完成后按回车键继续...")
    input()
    return driver

def get_law_data(driver):
    """
    获取当前页面的法律数据
    """
    # 等待页面加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.el-table__body-wrapper"))
    )
    time.sleep(2)
    
    laws_data = []
    items = driver.find_elements(By.CSS_SELECTOR, "div.fb-common-article")
    print(f"找到 {len(items)} 条法律法规")
    
    # 如果当前页面没有数据，直接返回空列表
    if len(items) == 0:
        return []
    
    for item in items:
        try:
            data = {}
            
            # 获取标题
            title_element = item.find_element(By.CSS_SELECTOR, "div > p > a")
            data['标题'] = title_element.text.strip()
            
            # 获取时间
            try:
                date_element = item.find_element(By.CSS_SELECTOR, "p > span:nth-child(5)")
                data['时间'] = date_element.text.strip()
            except:
                data['时间'] = "未找到时间"
            
            print(f"获取到法规: {data['标题']}")
            laws_data.append(data)
            
        except Exception as e:
            print(f"处理条目时出错: {str(e)}")
            continue
    
    return laws_data

def click_next_page(driver):
    """
    点击下一页按钮
    """
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.btn-next")
        if "disabled" in next_button.get_attribute("class"):
            print("已到达最后一页")
            return False
        
        # 使用JavaScript点击，更可靠
        driver.execute_script("arguments[0].click();", next_button)
        return True
    except Exception as e:
        print(f"点击下一页出错: {str(e)}")
        return False

def has_next_page(driver):
    """
    检查是否有下一页
    """
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.btn-next")
        return not ("disabled" in next_button.get_attribute("class"))
    except:
        return False

def save_to_excel(data, filename):
    """
    保存数据到Excel文件
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 添加序号
    for i, item in enumerate(data, 1):
        item['序号'] = i
    
    # 指定列的顺序
    columns = ['序号', '标题', '时间']
    df = pd.DataFrame(data)[columns]
    
    # 保存为Excel文件
    df.to_excel(filename, index=False, encoding='utf-8')
    print(f"\n数据已保存到: {filename}")
    print(f"共保存 {len(df)} 条记录")
    print("\n预览前5条记录:")
    print(df.head())

def get_output_filename():
    """
    获取用户输入的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"法律法规数据_{timestamp}.xlsx"
    print(f"\n请输入要保存的文件名 (直接回车则使用默认文件名: {default_name}):")
    filename = input().strip()
    
    # 如果用户没有输入，使用默认文件名
    if not filename:
        filename = default_name
    
    # 确保文件名以.xlsx结尾
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
        
    return filename

def print_instructions():
    """
    打印操作说明
    """
    print("\n=== 操作说明 ===")
    print("1. 输入 'n' 爬取当前页面数据并自动翻到下一页")
    print("2. 如果出现验证码，处理完验证码后再次输入 'n'")
    print("3. 输入 'm' 只爬取当前页面，不自动翻页")
    print("4. 输入 'p' 手动翻页，不爬取当前页面")
    print("5. 输入 'q' 结束爬取并保存数据")
    print("==============")

def main():
    try:
        print("正在启动浏览器...")
        driver = setup_browser()
        driver = open_website(driver)
        
        # 获取用户输入的文件名
        output_filename = get_output_filename()
        output_dir = os.path.dirname(os.path.abspath(__file__))  # 使用脚本所在目录
        full_path = os.path.join(output_dir, output_filename)
        
        print_instructions()
        
        all_laws_data = []
        page = 1
        
        while True:
            command = input(f"\n当前第 {page} 页 - 输入命令 (n/m/p/q): ").strip().lower()
            
            if command == 'q':
                print("手动结束爬取")
                break
                
            elif command == 'n':
                # 爬取当前页并自动翻页
                print(f"\n正在爬取第 {page} 页...")
                
                page_data = get_law_data(driver)
                
                if page_data:
                    all_laws_data.extend(page_data)
                    print(f"已获取 {len(page_data)} 条记录，累计 {len(all_laws_data)} 条")
                else:
                    print("当前页未获取到数据，请检查页面")
                
                if has_next_page(driver):
                    print("\n正在自动翻到下一页...")
                    if click_next_page(driver):
                        print("已翻到下一页，如有验证码请处理后继续")
                        page += 1
                    else:
                        print("翻页失败，请手动翻页")
                else:
                    print("已到达最后一页")
                    
            elif command == 'm':
                # 只爬取当前页，不翻页
                print(f"\n只爬取第 {page} 页...")
                
                page_data = get_law_data(driver)
                
                if page_data:
                    all_laws_data.extend(page_data)
                    print(f"已获取 {len(page_data)} 条记录，累计 {len(all_laws_data)} 条")
                else:
                    print("当前页未获取到数据，请检查页面")
                
            elif command == 'p':
                # 只翻页，不爬取
                if has_next_page(driver):
                    print("\n正在自动翻到下一页...")
                    if click_next_page(driver):
                        print("已翻到下一页，如有验证码请处理后继续")
                        page += 1
                    else:
                        print("翻页失败，请手动翻页")
                else:
                    print("已到达最后一页")
                
            else:
                print("无效的命令，请重新输入")
        
        if all_laws_data:
            # 保存数据到用户指定的文件
            save_to_excel(all_laws_data, full_path)
            print(f"\n文件已保存到: {os.path.abspath(full_path)}")
        else:
            print("未获取到任何数据")
        
        print("\n按回车键关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main() 