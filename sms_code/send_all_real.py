"""
전체 153개 전화번호에 실제 메시지를 발송하는 스크립트
테스트 문구 없이 진짜 메시지만 포함
"""
from bulk_send import bulk_send
import csv

# numbers.csv에서 모든 번호 읽기
def read_all_numbers():
    phone_numbers = []
    with open("numbers.csv", 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 헤더 스킵 ("Phone Number")
        for row in reader:
            if row and row[0].strip():
                # 숫자만 추출
                raw_num = row[0].strip()
                digits = "".join(filter(str.isdigit, raw_num))
                if digits:
                    phone_numbers.append(digits)
    return phone_numbers

# 실제 발송할 메시지 (테스트 문구 제외)
real_message = """U.S. colleges place the greatest importance on "fit." I hope you find a college that truly matches your child's strengths and personality. Please take a moment to check it out! 

Korean Shorts: https://youtube.com/shorts/RVlWrXZFv1g
Korean Blog: https://eliteprep4koreans.com/what-do-americas-top-50-universities-look-for-characteristics-and-preferred-student-profiles/

English Shorts: https://youtube.com/shorts/zcQRx4VKLmQ
English Blog: https://elite4usa.com/what-kind-of-students-do-top-50-u-s-universities-really-want/

Have questions? Contact Elite Prep Suwanee (Tel & Text: 470.253.1004 )

We have prepared a short survey to help identify the colleges that best fit your child.
If you're interested in receiving a personalized college list, please click the link below to participate.

     https://forms.gle/o4ri1mV5sMXz5D9EA"""

if __name__ == "__main__":
    # 모든 번호 읽기
    all_numbers = read_all_numbers()
    
    print("=" * 70)
    print("📱 Google Voice 대량 문자 발송 - 실제 발송 모드")
    print("=" * 70)
    print(f"\n📊 발송 정보:")
    print(f"   - 총 수신자 수: {len(all_numbers)}명")
    print(f"   - 메시지 길이: {len(real_message)}자")
    print(f"   - 예상 소요 시간: 약 {len(all_numbers) * 1.2:.0f}분 (번호당 평균 1.2분)")
    print(f"\n📝 메시지 미리보기:")
    print("-" * 70)
    print(real_message[:200] + "...")
    print("-" * 70)
    
    print(f"\n⚠️  중요 안내:")
    print(f"   - 전체 {len(all_numbers)}개 번호에 실제 메시지가 발송됩니다")
    print(f"   - 스팸 방지를 위해 메시지 간 45-90초 대기합니다")
    print(f"   - 20건마다 10분간 휴식합니다")
    print(f"   - 브라우저를 절대 닫지 마세요")
    print(f"   - 중단하려면 Ctrl+C를 누르세요")
    
    print("\n" + "=" * 70)
    input("⏸️  계속하려면 Enter 키를 누르세요... ")
    print("=" * 70)
    
    print("\n🚀 발송을 시작합니다...\n")
    
    # bulk_send 함수 호출
    bulk_send(
        phone_numbers=all_numbers,
        message_text=real_message,
        progress_callback=lambda msg: print(f"[진행] {msg}")
    )
    
    print("\n" + "=" * 70)
    print("✅ 전체 발송 완료!")
    print("=" * 70)
    print(f"\n총 {len(all_numbers)}개 번호에 발송을 시도했습니다.")
    print("Google Voice에서 발송 내역을 확인하세요.")
    print("\n" + "=" * 70)
