
from eiler.config import xlsx_path
import pandas as pd

def convert_xlsx_to_dict(file_path = xlsx_path) -> pd.DataFrame:
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        print('Ошибка с файлом .xlsx')
        return False

if __name__=='__main__':
    print(convert_xlsx_to_dict())


