from services.distress_service import calculate_distress

if __name__ == "__main__":
    result = calculate_distress(
        mood=4,
        stress=8,
        sleep=4,
        activity=5,
        text_indicator=7
    )
    print(result)
