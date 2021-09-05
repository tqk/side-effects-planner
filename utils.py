
import sys

USAGE = '\n\tUsage: python3 utils.py convert-plan <input> <output> <split action>\n'

def convert_plan(i_file, o_file, split):
    '''
    Converts a plan from the input file into a plan in the output file.
    '''
    with open(i_file, 'r') as f:
        lines = []
        for l in f.readlines():
            if split in l:
                break
            lines.append(l)
    with open(o_file, 'w') as f:
        for line in lines:
            f.write(line.replace(' )', ')').replace('__', '_').replace('_', ' '))

if __name__ == '__main__':
    # python3 utils.py convert-plan <input> <output> <split action>
    if len(sys.argv) != 5:
        print(USAGE)

    elif sys.argv[1] == 'convert-plan':
        convert_plan(sys.argv[2], sys.argv[3], sys.argv[4])