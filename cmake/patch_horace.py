import sys, os, re
import warnings

FUZZ = 10

def patch_files(diff_file, base_dir):
    # Patches files in `base_dir` with unified diff in `diff_file`
    with open(diff_file, 'r') as f:
       df = f.read()
    for diffs in df.split('diff'):
        if '@@' in diffs:
            filename = os.path.join(base_dir, diffs.split('+++ b/')[1].split('\n')[0])
            with open(filename, 'r') as f:
                t0 = f.read()
            t0 = t0.split('\n')
            for p in diffs.split('\n@@')[1:]:
                ll = p.split('\n')
                m = re.match(r'-(\d+),?(\d*) \+(\d+),?(\d*) @@', ll[0].strip())
                if not m:
                    raise ValueError(f'Invalid diff hunk header {ll[0]}')
                l0 = int(m.group(3))
                # Search for start of hunk in original file
                found = False
                for ii in range(l0 - FUZZ, l0 + FUZZ):
                    if t0[ii] == ll[1][1:] and t0[ii+1] == ll[2][1:] and t0[ii+2] == ll[3][1:]:
                        found = True
                        break
                if not found:
                    raise ValueError('Invalid Hunk:\n@@ %s' % ("\n".join(ll)))
                l1 = ii
                if t0[l1] != ll[1][1:]:
                    raise ValueError('File %s\nHunk failed: @@ %s' % (filename, "\n".join(ll)))
                for ii in range(1, len(ll)):
                    print(f'{ii, l1}: {ll[ii]}')
                    if 'No newline at end of file' in ll[ii]:
                        continue
                    if len(ll[ii]) < 1:
                        l1 += 1
                    elif ll[ii][0] == '-':
                        if t0[l1] == ll[ii][1:]:
                            t0.pop(l1)
                        else:
                            raise ValueError('Unmatched hunk: %s\n%s' % (t0[l1], ll[ii]))
                    elif ll[ii][0] == '+':
                        t0.insert(l1, ll[ii][1:])
                        l1 += 1
                    else:
                        if t0[l1] != ll[ii][1:]:
                            raise ValueError('Unmatched hunk: %s\n%s' % (t0[l1], ll[ii]))
                        l1 += 1
            with open(filename, 'w') as f:
                f.write('\n'.join(t0))


if __name__ == '__main__':
    # Recursively applies all diffs in a given folder w.r.t. an input base dir
    for root, _, files in os.walk(sys.argv[1]):
        for fl in [f for f in files if f.endswith('.diff')]:
            try:
                patch_files(os.path.join(root, fl), sys.argv[2])
            except ValueError as e:
                if 'Unmatched hunk' in str(e):  # Probably patched already
                    warnings.warn(str(e))
