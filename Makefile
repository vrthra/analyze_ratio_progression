nmutants=10000
nequivalents=10000
mutantlen=100000
nfaulty=1
nchecks=1
ntests=100000

all:
	for i in 1 10 100 1000; do \
		for j in 1 10 100 1000; do \
    echo nchecks=$$i nfaulty=$$j ; \
    make one nchecks=$$i nfaulty=$$j & \
  done; \
done
one: | data
	python3 mutants.py --mutantlen=$(mutantlen) --nmutants=$(nmutants) --nequivalents=${nequivalents} --nfaulty=$(nfaulty) --ntests=$(ntests) --nchecks=$(nchecks)

data:; mkdir -p data
