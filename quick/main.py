import sys
from quick_sort import quick_sort, quick_sort_inplace


def main():
    print("=" * 50)
    print(" [Quick Sort] 알고리즘 실습 프로젝트")
    print(f" 파이썬 인터프리터: {sys.executable}")
    print("=" * 50)

    # 1. 일반 quick_sort 테스트
    sample_data = [38, 27, 43, 3, 9, 82, 10, 19, 50, 12]
    print(f"\n[원본 배열]    : {sample_data}")

    sorted_data = quick_sort(sample_data)
    print(f"[기본 퀵 정렬] : {sorted_data}")

    # 2. 제자리 quick_sort_inplace 테스트
    inplace_data = sample_data.copy()
    quick_sort_inplace(inplace_data)
    print(f"[제자리 퀵 정렬]: {inplace_data}")

    print("\n 정렬 결과 검증:", "성공" if sorted_data == sorted(sample_data) else "실패")
    print("=" * 50)


if __name__ == "__main__":
    main()
