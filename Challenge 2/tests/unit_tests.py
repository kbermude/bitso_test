import pandas as pd
import unittest

def transform_data_events(data_events):
    # Date transformation
    data_events['event_timestamp'] = pd.to_datetime(data_events['event_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    return data_events

class TestTransformations(unittest.TestCase):
    def test_transform_data_events(self):
        # Sample data
        test_data_events = pd.DataFrame({
            'id': [1, 2],
            'event_timestamp': ['2023-10-01 12:00:00.000000', '2023-10-01 13:00:00.000000']
        })
        
        #Trasnformation
        transformed_data_events = transform_data_events(test_data_events)
        
        # Check the transformation
        self.assertTrue('event_timestamp' in transformed_data_events.columns)
        self.assertEqual(str(transformed_data_events['event_timestamp'].dtype), 'datetime64[ns]')

if __name__ == '__main__':
    unittest.main()
