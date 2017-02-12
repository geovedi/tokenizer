#!/bin/sed -f

# Preprocess
s=^= =g
s=$= =g

# Detokenize
s= ￭'\([sSmMdD]\) ='\1 =g
s= ￭'ll ='ll =g
s= ￭'re ='re =g
s= ￭'ve ='ve =g
s= ￭n't =n't =g
s= ￭'LL ='LL =g
s= ￭'RE ='RE =g
s= ￭'VE ='VE =g
s= ￭N'T =N'T =g
s=￭ ￭==g
s=￭ ==g
s= ￭==g

# Postprocess
s=  *= =g
s=^ ==g
s= $==g
