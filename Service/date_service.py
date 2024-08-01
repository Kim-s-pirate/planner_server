from datetime import date, datetime

class date_service:

    @staticmethod
    def get_date(date_obj):
        if isinstance(date_obj, datetime):
            return date_obj.strftime('%Y-%m-%d')
        elif isinstance(date_obj, str):
            try:
                # 문자열이 'YYYY-MM-DD' 형식으로 되어 있다고 가정하고, 이를 datetime으로 변환
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                # 문자열이 올바른 형식이 아닐 경우 None을 반환
                return None
        return None