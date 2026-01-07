import numpy as np

def fit_decay(p_user):
    p_user = np.array(p_user, dtype=float)
    i = np.arange(1, len(p_user)+1)
    logp = np.log(p_user)
    m = np.sum(i*logp)/np.sum(i**2)
    b = np.exp(m) 
    h = np.log(b)/m
    return b, h


def main():

    penalties = [85,70,60,55] # as 1-100 numbers
    
    penalties = [penalty/100.0 for penalty in penalties]

    b, h = fit_decay(penalties)
    for i in range(1, 21):
        p=b**(i/h)
        print(f"osoba nr.{i:2d}: {p*100:6.2f}%")

if __name__ == "__main__":
    main()
