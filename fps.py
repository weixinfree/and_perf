from subprocess import check_output
import re
from typing import Sequence, Tuple
import operator
import math


def _gfx(cmd: str) -> str:
    return check_output(f'adb shell dumpsys gfxinfo {cmd}', shell=True).decode('utf-8')


def _gfxinfo(file: str) -> str:
    return open(file, encoding='utf-8').read()


Frame = Tuple[int, int]


def _extract_histogram(gfxinfo: str) -> Sequence[Frame]:
    items = re.search(r'HISTOGRAM:(.*)', gfxinfo).group(1)
    items = items.strip().split()

    for item in items:
        cost, count = item.strip().split('=')
        if int(count) > 0:
            yield int(cost[:-2]), int(count)


class Fps:

    def reset(self, pkg: str):
        return _gfx(f'{pkg} reset > /dev/null')

    def collect(self, pkg: str):
        return _gfx(pkg)

    def stat(self, gfxfile: str):
        print(re.search(r'Stats since.*?HISTOGRAM', _gfxinfo(gfxfile), re.M | re.DOTALL).group())

    def fps(self, gfxfile: str):
        frames = list(_extract_histogram(_gfxinfo(gfxfile)))
        if not frames:
            return

        renderd_frames = sum(count for _, count in frames)

        def jank(cost, count) -> int:
            if cost <= 17:
                return 0
            else:
                return count * int(math.ceil(cost / 17.0)) - 1

        jank_frames = sum(jank(cost, count) for cost, count in frames)
        print(f'fps: {int(60 * renderd_frames / (renderd_frames + jank_frames))}')

    def histogram(self, gfxfile: str, sort_by_count: bool = False, sort_by_cost: bool = False, reverse: bool = False):
        gfxinfo = _gfxinfo(gfxfile)
        frames = list(_extract_histogram(gfxinfo))

        if sort_by_cost:
            frames.sort(key=operator.itemgetter(0), reverse=reverse)

        if sort_by_count:
            frames.sort(key=operator.itemgetter(1), reverse=reverse)

        max_count = max(count for _, count in frames)
        scale = max(max_count // 80, 1)

        for cost, count in frames:
            progress = max(1, count // scale)
            _cost = str(cost) + "ms"
            print(f'{_cost:>6}: {"=" * progress} {count}')


if __name__ == '__main__':
    import fire
    fire.Fire(Fps)
