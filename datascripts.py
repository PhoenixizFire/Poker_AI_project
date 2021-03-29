def link_phases(df_list:list()):
    for x,y in enumerate(df_list):
        print(x)
        if x==0:
            df_join = y
        else:
            df_join = df_join.join(y,on='gameID',how='left',lsuffix='PHASE'+str(x+1),rsuffix='PHASE'+str(x+2))

    return df_join