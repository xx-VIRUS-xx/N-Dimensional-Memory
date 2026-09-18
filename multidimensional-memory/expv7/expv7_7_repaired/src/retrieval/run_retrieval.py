#!/usr/bin/env python3
import argparse
from .common import write_result

def main():
    p=argparse.ArgumentParser(description='EXP-V7.7 repaired deterministic retrieval runner')
    p.add_argument('--condition',required=True,choices=['raw','bm25','semantic','hybrid'])
    p.add_argument('--top-k',type=int,default=24)
    a=p.parse_args(); write_result(a.condition,a.top_k)
if __name__=='__main__': main()
