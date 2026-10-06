import math


class CentroidTracker:
    """Simple tracker: frame-to-frame nearest centroid match."""

    def __init__(self, max_distance=100):
        self.next_id = 1
        self.tracks = {}
        self.max_distance = max_distance

    def update(self, centers):
        new_tracks = {}
        remaining = list(self.tracks.items())
        for (cx, cy) in centers:
            best_id, best_dist = None, 1e9
            for tid, (tx, ty) in remaining:
                d = math.hypot(cx - tx, cy - ty)
                if d < best_dist:
                    best_id, best_dist = tid, d
            if best_id is not None and best_dist < self.max_distance:
                new_tracks[best_id] = (cx, cy)
                remaining = [(tid, c) for tid, c in remaining if tid != best_id]
            else:
                new_tracks[self.next_id] = (cx, cy)
                self.next_id += 1
        self.tracks = new_tracks
        return list(self.tracks.keys())