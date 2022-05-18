
import argparse

handlers = {
    'sum': lambda x, y: x + y,
    'sub': lambda x, y: x - y,
    'mul': lambda x, y: x * y,
    'div': lambda x, y: x / y
}

parser = argparse.ArgumentParser(description='Calculator')
parser.add_argument('-v', '--verbose', action='store_true', default=False)

subparser = parser.add_subparsers(dest='command')

sum_parser = subparser.add_parser('sum', help='Sum two numbers')
sum_parser.add_argument('x', type=int)
sum_parser.add_argument('y', type=int)

sub_parser = subparser.add_parser('sub', help='Add two numbers')
sub_parser.add_argument('x', type=int)
sub_parser.add_argument('y', type=int)


div_parser = subparser.add_parser('div', help='Sub two numbers')
div_parser.add_argument('x', type=int)
div_parser.add_argument('y', type=int)

mul_parser = subparser.add_parser('mul', help='Mul two numbers')
mul_parser.add_argument('x', type=int)
mul_parser.add_argument('y')

args = parser.parse_args()

handler = handlers[args.command]

print('result=', handler(args.x, args.y))