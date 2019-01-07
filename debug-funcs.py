### Debug functions

## for packet-gen












## for schc-comp

#check for possible multi-reference 

#'''
def chkmultiref(lst, onedim=False):
    
    for i in range(len(lst)):
        if onedim:
            print lst[i] is lst[i%len(lst)]
            continue
        for h in range(len(lst[0])):
            for l in range(len(lst[0])):
                if l<=h:
                    continue
                else:
                    print(lst[i][h] is lst[i][l%len(lst[0])])
#'''

#check for equality between elements 

#'''
def chkequality(lst, onedim=False):
    
    for i in range(len(lst)):
        if onedim:
            print lst[i] is lst[i%len(lst)]
            continue
        for h in range(len(lst[0])):
            for l in range(len(lst[0])):
                if l<=h:
                    continue
                else:
                    print(lst[i][h] == lst[i][l%len(lst[0])])
#'''
