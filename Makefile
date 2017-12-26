nmutants=10000
nequivalents=0
mutantlen=100000
nfaulty=1
nchecks=1
ntests=1

all: | data
	python3 mutants.py --mutantlen=$(mutantlen) --nmutants=$(nmutants) --nequivalents=${nequivalents} --nfaulty=$(nfaulty) --ntests=$(ntests) --nchecks=$(nchecks)

data:; mkdir -p data
