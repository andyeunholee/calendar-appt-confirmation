"""
상세 디버깅 - 201-274-6707 번호로 메시지 입력 필드 찾기
"""
import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.getcwd(), 'playwright_user_data')
TEST_NUMBER = "2012746707"
TEST_MESSAGE = "Debug test message"

def debug_send():
    with sync_playwright() as p:
        print("브라우저 실행 중...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            slow_mo=500  # 천천히 실행
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # 1. 메시지 페이지로 이동
            print("\n1. Google Voice 메시지 페이지로 이동...")
            page.goto("https://voice.google.com/u/0/messages")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            # 2. "Send new message" 버튼 클릭
            print("\n2. 'Send new message' 버튼 클릭...")
            page.click('div[aria-label="Send new message"]')
            time.sleep(3)
            
            # 3. 전화번호 입력
            print(f"\n3. 전화번호 입력: {TEST_NUMBER}")
            page.fill('input[placeholder="Type a name or phone number"]', TEST_NUMBER)
            time.sleep(3)
            
            # 4. 수신자 확인
            print("\n4. 수신자 확인 (ArrowDown + Enter)...")
            page.keyboard.press("ArrowDown")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(5)  # 대화창이 로드될 때까지 충분히 대기
            
            print("\n" + "="*70)
            print("대화창 로드 완료. 페이지 분석 중...")
            print("="*70)
            
            # 5. 페이지의 모든 textarea 찾기
            print("\n5. 페이지의 모든 <textarea> 요소:")
            textareas = page.query_selector_all("textarea")
            print(f"   총 {len(textareas)}개 발견")
            for i, ta in enumerate(textareas):
                try:
                    placeholder = ta.get_attribute("placeholder") or "(없음)"
                    aria_label = ta.get_attribute("aria-label") or "(없음)"
                    is_visible = ta.is_visible()
                    print(f"   [{i}] visible={is_visible}, placeholder='{placeholder}', aria-label='{aria_label}'")
                except:
                    print(f"   [{i}] (정보 가져오기 실패)")
            
            # 6. 페이지의 모든 contenteditable div 찾기
            print("\n6. 페이지의 모든 contenteditable div:")
            editables = page.query_selector_all("div[contenteditable='true']")
            print(f"   총 {len(editables)}개 발견")
            for i, div in enumerate(editables):
                try:
                    aria_label = div.get_attribute("aria-label") or "(없음)"
                    is_visible = div.is_visible()
                    print(f"   [{i}] visible={is_visible}, aria-label='{aria-label}'")
                except:
                    print(f"   [{i}] (정보 가져오기 실패)")
            
            # 7. 실제로 보이는 입력 필드 찾기
            print("\n7. 실제로 보이는(visible) 입력 필드만 필터링:")
            visible_inputs = []
            
            for ta in textareas:
                try:
                    if ta.is_visible():
                        visible_inputs.append(("textarea", ta))
                except:
                    pass
            
            for div in editables:
                try:
                    if div.is_visible():
                        visible_inputs.append(("div", div))
                except:
                    pass
            
            print(f"   총 {len(visible_inputs)}개의 보이는 입력 필드")
            
            if len(visible_inputs) == 0:
                print("\n   ❌ 보이는 입력 필드가 없습니다!")
                print("   스크린샷을 저장합니다...")
                page.screenshot(path="debug_no_input_field.png")
            else:
                print(f"\n   ✓ {len(visible_inputs)}개의 입력 필드를 찾았습니다.")
                print("\n8. 첫 번째 보이는 입력 필드에 메시지 입력 시도...")
                
                input_type, input_element = visible_inputs[0]
                print(f"   타입: {input_type}")
                
                # 클릭하고 입력
                input_element.click()
                time.sleep(1)
                page.keyboard.type(TEST_MESSAGE, delay=50)
                time.sleep(2)
                
                page.screenshot(path="debug_message_typed.png")
                print("   ✓ 메시지 입력 완료")
                print("   스크린샷 저장: debug_message_typed.png")
                
                # Enter로 전송
                print("\n9. Enter 키로 전송...")
                page.keyboard.press("Enter")
                time.sleep(3)
                
                page.screenshot(path="debug_message_sent.png")
                print("   스크린샷 저장: debug_message_sent.png")
            
            print("\n" + "="*70)
            print("디버깅 완료! 브라우저를 10초 후 닫습니다...")
            print("="*70)
            time.sleep(10)
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="debug_error.png")
            time.sleep(10)
        finally:
            context.close()

if __name__ == "__main__":
    debug_send()
