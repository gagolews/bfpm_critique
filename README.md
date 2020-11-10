# A Critique of the *Bounded Fuzzy Possibilistic Method* — Supplementary Files

The ``Bounded Fuzzy Possibilistic Method'' (BFPM)
was recently introduced in doi:10.1016/j.fss.2019.07.011.
I demonstrate that there are some critical
flaws in the proposed algorithm, which makes the results presented therein
highly questionable.
In particular, the method may generate meaningless cluster
membership degrees or even fail to converge when run on some
classical benchmark data sets.


`bfpm.py` implements both the BFPM as well as the (now-classic)
Fuzzy c-means method (FCM).
The implementation of the BFPM is straightforward, because
it is an arbitrary (faulty) modification of the FCM.




## References

H. Yazdani, Bounded fuzzy possibilistic method,
*Fuzzy Sets and Systems* **389** (2020) 51-65. doi:10.1016/j.fss.2019.07.011

J. Bezdek, R. Ehrlich, W. Full, FCM: The fuzzy c-means clustering algorithm,
*Computers & Geosciences* **10** (1984) 191-203. doi:10.1016/0098-3004(84)90020-7

M. Gagolewski, A Critique of the Bounded Fuzzy Possibilistic Method,
under review.