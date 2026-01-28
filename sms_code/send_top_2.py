"""
상위 2개 전화번호에만 테스트 문자를 보내는 스크립트
"""
from bulk_send import bulk_send

# 테스트할 상위 2개 번호
test_numbers = [
    "7143003245",  # 714-300-3245
    "4702531004"   # 470-253-1004
]

# 테스트 메시지
test_message = """안녕하세요! 테스트 메시지입니다.

U.S. colleges place the greatest importance on "fit." I hope you find a college that truly matches your child's strengths and personality. Please take a moment to check it out! 

Korean Shorts: https://youtube.com/shorts/RVlWrXZFv1g
Korean Blog: https://eliteprep4koreans.com/what-do-americas-top-50-universities-look-for-characteristics-and-preferred-student-profiles/

English Shorts: https://youtube.com/shorts/zcQRx4VKLmQ
English Blog: https://elite4usa.com/what-kind-of-students-do-top-50-u-s-universities-really-want/

Have questions? Contact Elite Prep Suwanee (Tel & Text: 470.253.1004 )

We have prepared a short survey to help identify the colleges that best fit your child.
If you're interested in receiving a personalized college list, please click the link below to participate.

     https://forms.gle/o4ri1mV5sMXz5D9EA"""

if __name__ == "__main__":
    print("=" * 60)
    print("상위 2개 번호에 테스트 문자 발송 시작")
    print("=" * 60)
    print(f"\n발송 대상:")
    for i, num in enumerate(test_numbers, 1):
        print(f"  {i}. {num}")
    print(f"\n메시지 길이: {len(test_message)} 자")
    print("\n브라우저가 곧 열립니다...")
    print("-" * 60)
    
    # bulk_send 함수 호출
    bulk_send(
        phone_numbers=test_numbers,
        message_text=test_message,
        progress_callback=lambda msg: print(f"[진행상황] {msg}")
    )
    
    print("\n" + "=" * 60)
    print("테스트 발송 완료!")
    print("=" * 60)
