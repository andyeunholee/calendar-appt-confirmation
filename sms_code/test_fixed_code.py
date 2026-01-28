"""
수정된 코드를 테스트 - 실패했던 번호로 재시도
"""
from bulk_send import bulk_send

# 이전에 실패했던 번호로 테스트
test_numbers = [
    "2012746707",  # 201-274-6707 (이전 실패)
]

# 짧은 테스트 메시지
test_message = """Test message - 수정된 코드 테스트

This is a test to verify the new "Send new message" button method works correctly."""

if __name__ == "__main__":
    print("=" * 60)
    print("수정된 코드 테스트 - 이전 실패 번호로 재시도")
    print("=" * 60)
    print(f"\n테스트 번호: {test_numbers[0]}")
    print("\n브라우저가 곧 열립니다...")
    print("-" * 60)
    
    # bulk_send 함수 호출
    bulk_send(
        phone_numbers=test_numbers,
        message_text=test_message,
        progress_callback=lambda msg: print(f"[진행] {msg}")
    )
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
