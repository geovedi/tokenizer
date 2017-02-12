#!/bin/sed -f

# Preprocess
s=^= =g
s=$= =g
s=[«»“”„‟『』]="=g
s=[`ʼ‘’‚‛‹›「」]='=g
s=…=...=g
s=[—–]= -- =g
s= - = -- =g
s= / =/=g
s=;=; =g
s=' s ='s =g
s=\(\.\.\{1,\}\)= \1 =g


# Tokenize
s=\([[:alnum:]]\)\([[:punct:]]\{1,\}\) =\1 ￭\2 =g
s= \([[:punct:]]\{1,\}\)\([[:alnum:]]\)= \1￭ \2=g

## aggresive
s=\([[:alnum:]]\)\([[:punct:]]\{1,\}\)\([[:alnum:]]\)=\1 ￭\2￭ \3=g
s= ￭'￭ \([sSmMdD]\) = ￭'\1 =g
s= ￭'￭ ll = ￭'ll =g
s= ￭'￭ re = ￭'re =g
s= ￭'￭ ve = ￭'ve =g
s=n ￭'￭ t = ￭n't =g
s= ￭'￭ LL = ￭'LL =g
s= ￭'￭ RE = ￭'RE =g
s= ￭'￭ VE = ￭'VE =g
s=N ￭'￭ T = ￭N'T =g

## non-aggresive
#s='\([sSmMdD]\) = ￭'\1 =g
#s='ll = ￭'ll =g
#s='re = ￭'re =g
#s='ve = ￭'ve =g
#s=n't = ￭n't =g
#s='LL = ￭'LL =g
#s='RE = ￭'RE =g
#s='VE = ￭'VE =g
#s=N'T = ￭N'T =g


# Postprocess
s=  *= =g
s=^ ==g
s= $==g
