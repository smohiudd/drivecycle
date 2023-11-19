from pathlib import Path
import pytest
from drivecycle import route, simplification
import pandas as pd

dir = "data"
ROOT = Path(__file__).parents[1]
DATA_PATH = ROOT / "tests" / "data"


class TestRoute:

    stop_params = {
        "bus_stop":60,
        "tertiary":120,
        "secondary":180,
    }

    @pytest.mark.parametrize("path", DATA_PATH.rglob("*.json"))
    def test_route_100(self, path):
        df = pd.read_json(path)
        df1 = simplification.cluster_nodes(df,100) 
        tvq = route.sequential(df1,self.stop_params, step=2, a_max=2)

    @pytest.mark.parametrize("path", DATA_PATH.rglob("*.json"))
    def test_route_50(self, path):
        df = pd.read_json(path)
        df1 = simplification.cluster_nodes(df,50) 
        tvq = route.sequential(df1,self.stop_params, step=2, a_max=2)
    
    @pytest.mark.parametrize("path", DATA_PATH.rglob("*.json"))
    def test_route_30(self, path):
        df = pd.read_json(path)
        df1 = simplification.cluster_nodes(df,30) 
        tvq = route.sequential(df1,self.stop_params, step=2, a_max=2)

    # @pytest.mark.skip(reason="buffer too small")
    @pytest.mark.parametrize("path", DATA_PATH.rglob("*.json"))
    def test_route_20(self, path):
        df = pd.read_json(path)
        df1 = simplification.cluster_nodes(df,20) 
        tvq = route.sequential(df1,self.stop_params, step=2, a_max=2)
    