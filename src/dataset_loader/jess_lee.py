import os
import random

from typing import Dict, Iterator, List, Tuple


def _iter_text_files(data_dir: str) -> Iterator[str]:
    if not os.path.isdir(data_dir):
        return
    for name in sorted(os.listdir(data_dir)):
        if not name.lower().endswith(".txt"):
            continue
        yield os.path.join(data_dir, name)


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _split_into_paragraphs(text: str) -> List[str]:
    """
    Split plain text into paragraphs, using blank lines as separators.

    All text belongs to a single speaker (target persona), so we simply
    group contiguous non-empty lines into paragraph-level segments.
    """

    paragraphs: List[str] = []
    buffer: List[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        paragraph = " ".join(ln.strip() for ln in buffer if ln.strip() != "").strip()
        if paragraph:
            paragraphs.append(paragraph)
        buffer = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.strip() == "":
            flush_buffer()
            continue
        buffer.append(line)

    flush_buffer()
    return paragraphs


def _collect_segments_per_file(data_dir: str) -> Dict[str, List[str]]:
    segments_per_file: Dict[str, List[str]] = {}
    for path in _iter_text_files(data_dir):
        try:
            text = _read_file(path)
            segments_per_file[path] = _split_into_paragraphs(text)
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            continue
    return segments_per_file


def _batch_segments_by_words(segments: List[str], max_words_per_batch: int) -> List[List[str]]:
    if max_words_per_batch <= 0:
        raise ValueError("max_words_per_batch must be > 0")

    batches: List[List[str]] = []
    current_batch: List[str] = []
    current_words = 0

    for segment in segments:
        seg_words = len(segment.split())

        if current_batch and current_words + seg_words > max_words_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_words = 0

        current_batch.append(segment)
        current_words += seg_words

        if current_words >= max_words_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_words = 0

    if current_batch:
        batches.append(current_batch)

    return batches


def _train_test_split_batches(
    batches: List[List[str]], train_ratio: float
) -> Tuple[List[List[str]], List[List[str]]]:
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be between 0 and 1")
    n_train = int(len(batches) * train_ratio)
    return batches[:n_train], batches[n_train:]


def load_dataset(
    data_dir: str,
    max_words_per_batch: int = 2000,
    train_ratio: float = 0.5,
    val_ratio: float = 0.2,
) -> tuple[List[List[str]], List[List[str]], List[List[str]]]:
    """
    Build single-speaker batches for the jess_lee dataset (entire text is the target persona).

    Returns a tuple of (train_set, test_set, validation_set), where each set is a
    list of batches and each batch is a list[str] of paragraph-level segments.
    """

    segments_per_file = _collect_segments_per_file(data_dir)

    nb_file_validation = int(len(segments_per_file) * val_ratio)

    flatten_segments = [
        segment
        for file_segments in list(segments_per_file.values())[: max(0, len(segments_per_file) - nb_file_validation)]
        for segment in file_segments
    ]
    batches = _batch_segments_by_words(flatten_segments, max_words_per_batch=max_words_per_batch)
    random.shuffle(batches)

    train_set, test_set = _train_test_split_batches(batches, train_ratio=train_ratio)

    validation_segments = [
        segment
        for file_segments in list(segments_per_file.values())[len(segments_per_file) - nb_file_validation :]
        for segment in file_segments
    ]
    validation_set = _batch_segments_by_words(validation_segments, max_words_per_batch=max_words_per_batch)

    print(
        "Number of words in train set: ",
        sum(len(segment.split()) for batch in train_set for segment in batch),
    )
    print(
        "Number of words in test set: ",
        sum(len(segment.split()) for batch in test_set for segment in batch),
    )
    print(
        "Number of words in validation set: ",
        sum(len(segment.split()) for batch in validation_set for segment in batch),
    )

    return train_set, test_set, validation_set


if __name__ == "__main__":
    tr, te, va = load_dataset("dataset/jess_lee", max_words_per_batch=2000, train_ratio=0.5, val_ratio=0.2)
    print(f"jess_lee batches -> train: {len(tr)}, test: {len(te)}, val: {len(va)}")


