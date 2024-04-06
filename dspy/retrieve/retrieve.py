import random
from typing import List, Optional, Union, Dict, Any

import dsp
from dspy.predict.parameter import Parameter
from dspy.primitives.prediction import Prediction


class Retrieve(Parameter):
    name = "Search"
    input_variable = "query"
    desc = "takes a search query and returns one or more potentially relevant passages from a corpus"

    def __init__(self, k=3):
        self.stage = random.randbytes(8).hex()
        self.k = k

    def reset(self):
        pass

    def dump_state(self):
        state_keys = ["k"]
        return {k: getattr(self, k) for k in state_keys}

    def load_state(self, state):
        for name, value in state.items():
            setattr(self, name, value)

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(self, query_or_queries: Union[str, List[str]], k: Optional[int] = None,**kwargs) -> Union[Prediction,List[Prediction]]:
        queries = [query_or_queries] if isinstance(query_or_queries, str) else query_or_queries
        queries = [query.strip().split('\n')[0].strip() for query in queries]

        # print(queries)
        # TODO: Consider removing any quote-like markers that surround the query too.
        k = k if k is not None else self.k
        passages = dsp.retrieveEnsemble(queries, k=k,**kwargs)
        if isinstance(passages[0],List):
            pred_returns = []
            for query_passages in passages:
                passages_dict = {key:[] for key in list(query_passages[0].keys()) if key!="tracking_idx"}
                for psg in query_passages:
                    for key,value in psg.items():
                        if key == "tracking_idx": continue
                        passages_dict[key].append(value)
                if "long_text" in passages_dict:
                    passages_dict["passages"] = passages_dict.pop("long_text")
                pred_returns.append(Prediction(**passages_dict))           
            return pred_returns
        elif isinstance(passages[0], Dict):
            #passages dict will contain {"long_text":long_text_list,"metadatas";metadatas_list...}
            passages_dict = {key:[] for key in list(passages[0].keys())}
            
            for psg in passages:
                for key,value in psg.items():
                    passages_dict[key].append(value)
            if "long_text" in passages_dict:
                passages_dict["passages"] = passages_dict.pop("long_text")
            return Prediction(**passages_dict)
        # elif isinstance(passages,List):
        #     return Prediction(passages=passages)
# TODO: Consider doing Prediction.from_completions with the individual sets of passages (per query) too.

class RetrieveThenRerank(Parameter):
    name = "Search"
    input_variable = "query"
    desc = "takes a search query and returns one or more potentially relevant passages followed by reranking from a corpus"

    def __init__(self, k=3):
        self.stage = random.randbytes(8).hex()
        self.k = k

    def reset(self):
        pass

    def dump_state(self):
        state_keys = ["k"]
        return {k: getattr(self, k) for k in state_keys}

    def load_state(self, state):
        for name, value in state.items():
            setattr(self, name, value)

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(self, query_or_queries: Union[str, List[str]], k: Optional[int] = None,**kwargs) -> Union[Prediction,List[Prediction]]:
        queries = [query_or_queries] if isinstance(query_or_queries, str) else query_or_queries
        queries = [query.strip().split('\n')[0].strip() for query in queries]

        # print(queries)
        # TODO: Consider removing any quote-like markers that surround the query too.
        k = k if k is not None else self.k
        passages = dsp.retrieveRerankEnsemble(queries, k=k,**kwargs)
        if isinstance(passages[0],List):
            pred_returns = []
            for query_passages in passages:
                passages_dict = {key:[] for key in list(query_passages[0].keys()) if key!="tracking_idx"}
                for psg in query_passages:
                    for key,value in psg.items():
                        if key == "tracking_idx": continue
                        passages_dict[key].append(value)
                if "long_text" in passages_dict:
                    passages_dict["passages"] = passages_dict.pop("long_text")
                pred_returns.append(Prediction(**passages_dict))           
            return pred_returns
        elif isinstance(passages[0], Dict):
            #passages dict will contain {"long_text":long_text_list,"metadatas";metadatas_list...}
            passages_dict = {key:[] for key in list(passages[0].keys())}
            
            for psg in passages:
                for key,value in psg.items():
                    passages_dict[key].append(value)
            if "long_text" in passages_dict:
                passages_dict["passages"] = passages_dict.pop("long_text")
            return Prediction(**passages_dict)
        