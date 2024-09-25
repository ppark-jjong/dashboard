import unittest
from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError
import googleApi


class TestGoogleApi(unittest.TestCase):
    @patch('googleApi.build')
    @patch('googleApi.service_account.Credentials.from_service_account_file')
    def test_get_sheet_data_success(self, mock_creds, mock_build):
        # 모의 데이터 설정
        mock_creds.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            'values': [['Header1', 'Header2'], ['Value1', 'Value2']]
        }

        # 성공적인 데이터 반환 테스트
        result = googleApi.get_sheet_data()
        self.assertEqual(result, [['Header1', 'Header2'], ['Value1', 'Value2']])

    @patch('googleApi.build')
    @patch('googleApi.service_account.Credentials.from_service_account_file')
    def test_get_sheet_data_http_error(self, mock_creds, mock_build):
        # 모의 HTTP 오류 설정
        mock_creds.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.side_effect = HttpError(
            resp=MagicMock(status=403), content=b'Forbidden')

        # HTTP 오류 처리 테스트
        result = googleApi.get_sheet_data()
        self.assertIsNone(result)

    @patch('googleApi.build')
    @patch('googleApi.service_account.Credentials.from_service_account_file')
    def test_get_sheet_data_unexpected_error(self, mock_creds, mock_build):
        # 모의 일반 오류 설정
        mock_creds.side_effect = Exception('Unexpected Error')

        # 일반 오류 처리 테스트
        result = googleApi.get_sheet_data()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
