"""fastText operator adapters."""

from typing import List, Optional

import pyarrow as pa

from core.curation.operator import (
    TaggerOperator,
    Operator,
    OperatorKind,
    OpContext,
)


class LanguageIdTagger(TaggerOperator):
    """Language ID tagger using fastText."""
    
    name: str = "lang_id"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.TAGGER
    
    def __init__(self, model_path: str = "lid.176.bin", threshold: float = 0.65):
        self.model_path = model_path
        self.threshold = threshold
        self._model = None
    
    def _load_model(self):
        """Load fastText model."""
        if self._model is None:
            import fasttext
            self._model = fasttext.load_model(self.model_path)
    
    def tag(self, batch: pa.RecordBatch) -> dict:
        """Tag batch with language IDs."""
        self._load_model()
        
        if 'text' not in batch.column_names:
            return {}
        
        texts = batch.column('text').to_pylist()
        languages = []
        lang_scores = []
        rejected = []
        
        for text in texts:
            if not text or len(text.strip()) == 0:
                languages.append("unknown")
                lang_scores.append(0.0)
                rejected.append(None)
                continue
            
            pred = self._model.predict(text.strip())
            lang, score = pred[0][0], pred[1][0]
            
            # Convert fastText label format (__label__en -> en)
            if lang.startswith("__label__"):
                lang = lang.replace("__label__", "")
            
            languages.append(lang)
            lang_scores.append(score)
            rejected.append(None)
        
        return {
            "lang": languages,
            "lang_score": lang_scores,
            "rejected": rejected,
        }


def register_fasttext_operators(registry) -> None:
    """Register fastText adapters with registry."""
    registry.register(LanguageIdTagger())
