from genericpath import exists
import pynmea2
import pandas as pd
import click


def msg_to_df(msg, prefix=''):
    lst = [(prefix+' '+f[0],msg.__getattr__(f[1])) for f in msg.fields]
    idx , val = zip(*lst)
    return pd.DataFrame([list(val)], columns = list(idx))

def append_evt(df, s):
    # cols = [(i, i in list(df.columns)) for i in list(s.columns)]
    # n, b = zip(*cols) 
    # if not all(b):
    #     for c in cols:
    #         if not c[1]:
    #             df.insert(loc=len(list(df.columns)), column = c[0], value = None)
    try:
        out = pd.concat([df,s])
    except BaseException as e:
        print("{}\n{}\n{}".format(e,df.columns,s.columns))
        return df

    return out
                

@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.File('wb'))
#@click.argument('filename', type=click.Path(exists=True))
def parse(input, output):
    """Print FILENAME if the file exists."""
    file = open(input, encoding='utf-8')
    df = pd.DataFrame()
    s = pd.Series(dtype='object')
    l=[]
    for line in file.readlines():
        try:
            if line[0] != '$':
                continue
            msg = pynmea2.parse(line)
            #print(repr(msg))
            if msg.talker == 'GP' and msg.sentence_type == 'RMC':
                if not s.empty:
                    df = append_evt(df, s)
                    #df = pd.concat([df, s])
                    s = pd.Series(dtype='object')
                    #print(df)
                s = msg_to_df(msg, 'GP')

            elif msg.talker == 'WI'and msg.sentence_type == 'MWV':
                s = pd.concat([s, msg_to_df(msg, 'WI')], axis=1)
            elif msg.talker == 'II'and msg.sentence_type == 'VHW':
                s = pd.concat([s, msg_to_df(msg, 'II')], axis=1)

        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue
    print(df)
    df.to_excel(output)



    

if __name__ == '__main__':
    parse()