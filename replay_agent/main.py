"""
Kaggriculture agent - v50: recorded-route backbone with live guards.

WHY A REPLAY. Twelve controlled experiments (EXPERIMENTS #48-#56) showed a third
quadrant loses for a COMPUTED policy: about half of all unit actions are spent
walking, the town's demand pool is fixed, and extra tiles just grow produce nobody
buys. Every 3-quadrant agent we could verify is a hard-coded action sequence, not a
policy, because the margin lives in per-step execution quality that a recorded expert
route has and a written policy does not.

SOURCE / ATTRIBUTION. The route is the player-0 action sequence of public episode
90598134 (final reward 110,596), taken from Kaggle's own published Kaggriculture
episodes dataset, which Kaggle released explicitly to support imitation learning and
bootstrapping. It is another competitor's play, not our own logic, and it is used here
as a behavioural backbone with that provenance stated.

WHAT IS OURS. The route was recorded BEFORE the 1.32.6/1.32.7 balance patches, so it
never exploits the new CARROT/TOMATO/EGG hinge curves and it sells in recorded order.
On top of the backbone this agent adds our own market layer: impact-ranked selling and
a terminal shed sweep (EXPERIMENTS #51).

GUARDS. A frozen trace scores near zero on unseen seeds, so every recorded action is
checked against live state: hands are aligned to the crew we actually have, and market
orders are dropped when the shed cannot supply them.

agent() must stay the LAST top-level function (kaggle_environments loads the last callable).
"""
import base64
import json
import zlib

from game_data import predicted_price, daily_demand, CROPS, ANIMALS

_SEED_COST = {c: spec["seed_cost"] for c, spec in CROPS.items()}
_ANIMAL_COST = {a: spec["cost"] for a, spec in ANIMALS.items()}

_ROUTE = json.loads(zlib.decompress(base64.b85decode(
    "c-rk<O^;hia{MoS?t@6SG?H&x>Fr9`9%-Nt6ZW7n7{I$QV5|>g-;Dk5)~K80<EzNXh^%5aHR>BhvEQrj%8ZPR{Q3Vb{{HK4|M=T)7yt6}#ZNCke!RH3y!g*w|NB4w=gSvgKK|p^-~Q`w|NHyre_pCT{rTd}+Yi&1|BXK+PuqVJe>i^OpFaQFFV`>Mz5e=x-~aJ(nqFUAUToh?FF##eUR^EU`0o9OPj8N2x%=wpi|zFB)7KA&ukJpv5&81|Py1IMcV_Wl;K9->wl6<TAC4cr`wBmD@nZ65Fdoy(yHRMH-+pt~4(|=&V~#(4osHVaFP~Bz9We0WWA1x+x>ja+`Ji34y1D;hyPMXBUR2Ru@z&Jf9rrjk=Q=hY-+#W_1?Mq1+HNim*=^$tTVnpl%Jo0im`HlvXXvzJ*lv@>H`XHVc^X@}?d7@rYTWJVJlR^3gRHsb${uG^kZn90`1EYMdklIo8jN&dkmq%c0D111L%ux;z(5!W6<BV&b7a>4{n65CJu!!3_YQDSmi8k#A%(qS9k}xHupV1k3_aJv<I^7GY1+ma+TuTbetZ4;moGp2^!e+}KFAUP{@(IU*eOdbP<q`ikNwN$wVsa(?ESDC)i&2|aILY;J#a>iL=S(ERsuV-w~>=zqAYCKDlmrTda`eN+P<{EJBM#r1Hl7X3-5kj9m0dZ+I(l(cjP(UPu!pA%}d5TFug3K=d}l9;o6KIGG9-H$1eW%4`X+9y78xQ?74G(Yw5gv_x8t^*I#U%SMRqMmzx{I)01CsE$5%!zWVFupAHQw_fPTUUrl!}I^k=G*@93H2D{%**-szdzyAE{;No2Vkk8t(uP2(kv5RBB6!vyFcIDfjW&aDm%x{N3|LzuOYY3RZhm)^)dwCFe-(S7FTWI@l?s~BMU@heR(`X!X@y=cohyjB=Z)j&F3@j8OwipQ;-v<;&FyePSR?Yg+>570!J!xNJclXq8)i75J43yG8>li=0Lz|V#D@Yg*d^2dIM&3qOCp7lji{{n)>+9*&r(ga&efaeD`t84ysaJnW`g(VWs{l{DCar_*&C3t}%2xM)j<o~ZT4lHy@nLI?<H1|wFWwmzv%X%gmp|Hn_D-t35pWneVw<-AMew{Y9h|POn|9}$6&M%vh;FxQU>rZggsleCJ&Y?b@8-Q(C3lm#L_+j;{y;eCM=wg31)Q0c#aaW1Koc`ttYIEw6Q*w?PM?TL&%#-G9M?L$)JwnfPU90E>>uTvfa~9yO>LlSzB9K!z?N`(+L}E3iJCusY4}!6#C-OS`c#@cw@U@gx_w34?82SpcBf#?QM~+cNzYqe!>D0jmauv7X*<d2I_M94Vu;*JZ+Tc77=j&;Rw`pY5M;Z%DDQsvyrFitR^8sB(%&2yv%%LKGRp4GV~}^<eEspwH2pODkHua4R3Pddp|<Oz#k)7{3fr_@1gSgFb1JkmD*&hHy7wJoeDW&*i3hJo{gLen@5%#2RKbC?Rs?tj^Z1nu2&{wM0-x^{exEMS@p^Iu_CfMrI7fSoZQu4d8{f=T^1VcGrGce`*J}IUf-iI#oTD#<mbHVmzY`9#5Cf<w1?kC+6&C=9?|#bK^EltxEbN?}Tm=R?2@B5e(8IMW<v&%<OE!>(M`Zd5%~?XB{;nh}8iNF9w!njQ^3+@eVOTbs=%p*S1z9zF{s6oo4m%^|DlC@&^9MD&*Q(*Y4!;x(@Ab29)$o26S=d6#3$d0%3(C6I57A-VV}K6tze-=%&Jc?l@Bh!3lOiYw*64mtj{dv3*NWIW2yo4>D-7<t9VR$BSS;wu-fG6t+5(Dal(fbyLX7~{sRsu?y(y#`A$%mXV)x^U=gylX;eGJvI&2&o2}@^Fpn0Kb0wx{ZEvA_rLH$pJwa3jvx8VlMgT}2qp9l_$5}|2*TpC0}R6r#*MD~=*<CuD49{?>FO4K8{VT^@j<QqALF=cO8{0vdsp?x&)J@h_PC!Y11OhP3U3r42eB)4UjUGW`+Nc{TkUuq`*i;*V(dBX6Ozos6<SvnB;AVg&C=5}z9dHkvn41$gap^pYFyt*+QlJ+jueU$wlGuTzVWPuxFO?qpEA6k{Nm<kKuaD;F|HFigmwX<*wEzY{d32N6L=tVHDksDoLEeRoMu!NDD(eA9w^HW!D+eq|&49;dj1cU~5sFlRNPxK$`XbKlGy4<0|so21jW=cqdp&7okc|gb0Rw~+K%w`S)m~6;(M=u4z6la~ZA2}b<R8$$nQ{*=4jK#D88aRK19msk@UQ0wW9Z$B@nmmlq55cW?>zmoSrp_3G7>Pqed@h~4K!E{)#vF{-&R^*{=@)U1OY{xf*I<OxbWA3GGm{Egpp!sug%4E0O#}(MZM+D1sS_T>inS#vVx_6Nmn@sv$!UA?FutuAW<E>b_A2j8!MEN2Nw+sk*;y6WR-CLuOlgnUtFzLgh$nG#slBl9u;=|agqD2zQs$?&A5^!&@k?PV9B$vKpclSVD(L_WS7BeZA4=*egp3yQ)9|m-MB%_&OFU34P#Hu^CJC~bZGT$^*K|bv|B$GOIS8Nx^P~uo7Bk8)71fWv3WI*n`dZI(d}8;B2w_BCDkSpLYa}Da;WUFB1gOO2h>O7qR~b5ya4U3};5h2Lx#?A%(u6ug$$@IaS2srPv!E8)pLZ`WTn73`+2-RU!f~b)pSEV9-nn%nRK>RnBT+iznPOJxy<HadlezB-3;>pvpZj$Z?%0~T%vw1*oU9lK(I5rgJ$MU(_iF@}E_($f0W=`E<)o>ZFTOh0IP*BxY2~lKL8j`!KyypNlJtQzFZ;g3%NfW~p`~^UY_y0k_rR^u)1e}cn#9CakY<8MsV^%kV?b(w)hJJy=1T=Z;>!-=9`n0t#BlP&%?jR5o&mSg__D~|$%D4mUP@4<5K@sS**Pk~kQ&WnN6F|kiJp<_0V$ydD_p9<1j_L<EoU-Ub=N(Is6ZshbRWHjSETSToIqO8O)OB(FyKURKp|6k@_EYgLM1ll{7}<GVl?#=MnHgt<ZcWpuB{|fWs<>-O!Xuk7qo>=ew73uB3TR?qEKBnXG(HRd%$R`Ovv}lu1l%OEUjM545gS%#U!RuhYV~9(`JkL0Bum7N#9A3V&;W!9=&ke3xD3>g~zS!^TL%;aJ=v;5~%6xv0d#u=g<Fm&Us7prJ<;TZ_aW`Q+7t`o@b+Hc<1E2?iVW+1CN%cUeR5k$O|xi2XOZRZcWt6Q_3aJHC?C7Ud^&*R-zv)uX*L`KEAR6<*?qiYlu-n;FfqPsjBKC1G1Vhl5<afsq|?G{KT2pU@LNOtiq~6)M2#=V+16H5PYU$$fflwRiwG^$98}0KNBUgp^3|0J;*6{a1y7Zi%FnW8=w<h6c0Awsu-8jVWEO>a1VPV*&Y^gpYA2e6K7F;DLGroyqEDP!L<m6kK#}GY$8{7P3ncQ>D#a3)NE<ufJESVlG@MLg?}orz8NDVZZN)^<UddAXc1q%m06WlI)8k7{ntB7uXO^!kB(wQmS>e*v}uc550izaSRyA^Y`pF4Y8{1mcK9kM-p7NvegFR28F85k^nAA*z8vANFUs6OM%35y=TirrdDXMt?{@ED(8Tnkc(&wpnG7F7?6xJxcGvLmtp9Pke*f;v3t!w6OduAxw;fw9YamX<rqT^Tt%^Y+Qo|ux{CEyZZQmJ8x6i<{6JRCq?+O{?sHn)|+1z_0ovBIEC(^MjCd)PD^EMYvI@WVKDr6n70jsMmaMU4RVB7`i8%1+mkoPck)K?%~j+3&(gJ|)no)N0gPve-OMOdMK(3d4eBS@q4Q3CTPsyp+gR4O}xk+AS>G+xcb2((jQu-nA)fEhPVU<K$iniN&hsyrsFk_vpdoirtP?W-cH(Oij7AI5nXq%9SvT>qOf52E!`R9R0sPe}@=r+$9HrN6S6k4oB>wyrBg_{O2-1puQ+H5A>_quC(z)H<ncq^$iA{YG(v5^Pw`mY3u3-q#sb-4un+=+FQ!5R?8vMGHk0M$QiRhK;(K?Yb#cHxne$wv!O%GXKLMcdSN|ds(d|8r)<#3;Za9VQrnn1zIKV(d~4vyN>FIi>VY0+A_AJ$6j#67pl9#C-3CPic;V^6m*s{K87eWNCx$#ST9=^^S`WmF-H7YPXDXqfpx}@FZF>J3Dw?QYrb7Jls4<T$S9B$+3Y&V{VDC7-XK&bFG~NhcovD!bCLXMP&6JW_i<(bgL`v_9(X{z_cEcO)<@g@l_694U`~5y=>5!`cfq4?`@f*xd-Y*v2VoYghk3e+KhMQl6>q<*ay*NEABT}Q!B^m*OOmTfQ>&o~2^_4*^s-X`msuu)cPJR`;UfD#ObDKmaB>?WolhiD8z~s;EUvv3vO-(gl`zsmM*KyI!~%wuR&OPa_ASP9#h+>oEQ@?|j(t9oqLm&|D-?xqP<aflXH5tQ2s#*p3z~<VS3#&vOA_uCN=_jr&OYbz*I;5sX)4k8s$+?mM07mN>=gk;D<)i1T%G)UQ28SD=wg|nU~zO;QeFwSHz}P<D+fyYB(dK=r0sNQ+x`gh^U2>u^+#-X4Y48+w~f{PO%BG;8eH)ywSqWeXp5C=;U|`=!>bYwNnO%Ju9N)^7<4K1(r`d-N~CwTq*LDKz8^W+gC-)`JEL7=Z1GUbA&#FcMgxRF3+I*QBx(t5ku{SkA4p|MhQtihVP-9-BGjz}nV>3qZV1pf%HQaLfEw!V0vdW!Qg~K59!XaTiJ^!IDc}!2JgEc&{ZFB{vhrIA>uJG*^d=EfQ3%z<V0M-C$pDH#s?BZ5WYWmEbCeym=xJ64s^!BVUdOPy2y_Ms2j|KtqSvm17FN4`>ZW-AD6Ei02cGIlEjq3c6&gw4QZ)M=0{y$O)YVV4iV;EzOCfhhIoterwpV{$fHJ^2p4Ws(;iu#gBegBucqesVY2o#paKY<}T6HE?r5cIUsclaar-r88w^i31igcKwx>7!sUGfMHwL;Wp@S-S=FJCMp8psi-CY02lQiLDp4M<{y;8^S_`kL#i_`LsE8YGi7NN+P1Fx=*HEW>DA7?YO-Fxjet!CU+o57F+V1u5h&r__`gWB?;@-!*Wg@*`QT6``cgFmMbWF*`yKin1t2oTN9+FQZb1zE*NgFcr`YwVbZ*%%`UGh}MCIxOKGQn>r-T&&wsa&kpkgi38sU>+5PWnn;||!4O@W4~J5^dmQpd=|6=3g@*%PvD@iBiC>_4nLzrYbsn+y(}`(cw8R1-dr@Lu<M_?sL}2vktS<=+wCG=$!=10yoC&tc*-A`Y+@*xk)D4ZSly>0hjiF6$u6a>jL(h)TbShQWK;nj$*kEk>Z8jMHu8>^<=9Vfgh*|O6j&tN%c+m~eR?4>ELF3@AO+kWoiUT)N$r4HEo>~@4sOn+|>Lq57801!JBqY$-Y$Q6Xk4o$*VT{wWjA%~k3h|5+MRh(TAz-C(O3^ln!6B(%dILxNP_RbRfI}MtrE6Xn?lie%WMQ%hs7LfGOgxXxCvX=}JH0hZ*78+dt(sG*_Z<--v)h<KnzR1)W~m1VodLAO@z}~@XX{2Q7Xg|EBr%dGb6q(5kzRFH^r}^h!L-Vhe<*qtu?Hx3s=XW@o>!HiU~=J`Y~SA(t*V_HkUbO|HyW3!oyfwetHtx%!2Sd9r%YllaF6r?N~A7HI{uFIu~#q@SQN5ZLX8lul!-%T6SIQ^LKHBwnNHJo$}0g^vzi#P)uUol6nDBu>QgQ%lUBDD>`r+xYpT(!F(rt3SqG|NF)5C&kR&#u(N3tJIb)V5A@kQxErgOp%7Q>YnZHin)22i&<n>nYNOSccafucSwuoLfrK3?nAhsw0lyu5^Lt<?iDN!3HEsE8mhA8q*A{9nD^n^sMAw0nhLlSCMO+v+R4jz;aEVkIS>SQeM9jLy_S>Boq7O$=-ise^I6H6Q;9<-w7wb0Jq*6n#fJn}~yw_^@bxa(U=7Q_sa?;Forzu<yBn<|Tl6=S(4IVn9Y4N)?1kT#=i($Hg%y7#P!8vLb{YvKBR^sr^jev+m(v>Tcp6jd;SmU&X3uvNm&S6b{`qP0iQWy!K2-nvX9qSv%mx|v>*ea$b{N#vV=3yU!m+|c(RIhh*yno+nKDjPustnnqT<d9my3ipgAj+PjR40yPG@H+E00G0@ro_Ab`L#umIKwm5j+LKZ4%Yj)Q!@P48qeXu}@8;t8a|#O>RjNqFcoO;GU-hJS(2VDVjtH{B=~?J4f07e6$G=0ohL9xKEtM-+(Jbz<8AOt&4Z?~r3dZUd<<5EQUrNdH`0(3LU=}6Qpj$(%lUs>Fwz($Xlt*RoR;W@WbD86nSbbXjz|mbjlc-#DRh4m&($Mlk4-_J;&YC05*hYQfCgLUlkTzWY=ZJEe?Q+Rg&T55tm>!IxC{kIBj})x)f~+<zWVLxA89XZfLWG*-QtbBtRkep7t^Cc3Ngxf>(`B?Zc0cb_UM?N@1;8=_BqyT^1u25W?$qR7Zml714CVwGQ4CQnmLz5ZaZQ4DAL;e$B(yImB7YTlWG&B3(Pyq%$V$LcOJ&m};2idpK(}FT2uc{GKos8#241E`ybP@<p4~<f%~8eQfYIBoToGH1kgHXyo+}ryGD@1Ms^$z^PrhM{F0vzp+%ubRL61jCvA%<i>IenXEH1mVxo_@@C$oZUa*ZrQBe~}M7)d;Qr(%SFYTuMuEe_Apz4$f#mvpcKGF6SJ2O`vl{*Xqm3V6pSk?XO`7>Xn~j%|-Gi{KX{7Zikq2!M|jc$p*x-FHUt6}gozV{CoXS?MIYb|n@fJ-Mq)P!^M9h<_5_XRGd!4D|;_mexP0DB)m^lq$0XaD&m%6Vzh}i7NXB<s2!Npg)!(WfaF^d!EuXVaLJmWT!o7JW2W^fQVY@5Za!|KU*%m0Wu#n?<qB@g@ml6&{_-gG-_AQLgICR=$bcGu(&Z@)Pf*R7r@0^f{d@ct_Vd{P+27<j6f|^_GF@x>y$TBs@NxEAL-T!$AYqK#GF6j)Jl!VGUZX-g4Kd(l0H8p&l>53WEGlwU9T|2ZfHkf9fttMIbnppEtNW?4zQ9d6VCQ9M_(fXO69#Z4eW%;GGvmNy^{IxS_(O{<4%E=xw02zP0>Zk`%(jrU^pN<n<-E%3VoE1Ul{|ZC>_sq(5Whhd>PI9r+6bTr7Fwz6MU~C++V<uHNv-8V6R_aDZ%jwZ4};eP83p}i()_YSf!I}%chi-v~X_0_1ROfa{lG_mNfW8oJv;ookKo|t)xL?ZvLQxi!xa_@d^ieKHOii6lRj_CylQYN`hM|L2l{2tIS$ta#f65mB5gBJE_t$y96i#L=t1cbvdHqA5DM^G}SlJt$n~6c`w^P$d#9gtF0A1*P+CmjYY=%hoYekN!==bk;>t~>>Rc#EvQf{z)7?IwiUyP_zklTcLF)UtwAI=Jt(Rk@^W~<wFg<M4oos2v(#R#1OO>XeMos6mWc~?l}F;M=Gkc{D_vctnvX2Zrsv&JpPpTUY$N44e15{6SLu(79<~M@-ybZD)-MvBlP9M{fF~i<0oDqLh!t5FR5ZyBkP$1ukZi}>RZ~KeWRhUV;!LetN~{;?%CjjrSB!JYv;||8yro;zQ=028nSR0y$C~h=c12L}s~X8N17XoErgPx33K=?~xfoh{Bxju)=ycVBPCuN8ghl;Go3`aZO<Sd$9ROu=u9d1#df#j-mM=szjS}jnWDExlhI=iiSu7)`GjK&@@6gFsa_5S7k7(9Vz8)(&<S?u*yClD(LCUi)ED^4p+)DsWO0;M}OI3p`lt1ay%tEXcZq-r=9G$kLP%45Y5;Im=6izJz!NrG!H|baj^$htzNs0T43bRmkL%|d%#gHbI6224!HkBNgT7tKV=qv0aw40gih=7BXbGzBfK-E)2B4L>372gK;FBZe_XX7-|I7<~SNK!SFl^@n+WMVG2aGk|m52|!$3&`sQ^E{CRGq+RKLMIluQa+CX+iW!T${QJ8CrPCUg((@2GSFt_@J;oU*i=-DDC(eV8^N2j9Xu<TuZhNKmAP<eCE+0(s46vDl3gxooYEZ7>gLxVYfhKQA*$@c38OkbJ@1h-bx!cr8WawEQnqje-N!sTP!wG!(7&b7($X75iC4MEUSF{|H%`P3TRQHoO_nDg7G*WEI(k&WM>oRKD{)*26EL!g_9;aX36WvBOnd2TtfDNlh+5~6UNh_5SguyOr)o*604Z~5nyJc^&J+MbkV{-;#rBvugUIb$KGmB9YDKfc8cuRR`bTEQ8DskN0A_+6<$0M^(W|W*B@o3IC#Bv7@w!wUURAT5rJ7GxT3Nofk`%mzon_>fw~vRU9#JtT_O$%vq?Vc`n^~&xMfz$b-BoXOre)f;ThJz5nc7lLBHk%eIRzy?T|ACuM3*Wa=mmVK%nz4?&r9fa!IIKUGXUGUuoQ&M)6l9(!7HS{JlAtlpuD>L_C}yYDF%R|UeC<y{g1vDx3fH23R@wxb60{-lP)uSz_x9>QhhljwQrU1i?{>3_Z`3YTav#*Y69OCK&5~l28)X4(Q@!fDRv~>3qMZR@85kTm5Ab1j0F-!coK5>k#?Uydxa8yQl5>P{jS#sn^Sl81MgTFST`$({U6h+_Vb+8Yis6r_Lp0ku%B)XE?qM@h5z!|G)ww5v$R?p>}0rr#6q^1$rSIHPLd&53A5Qwwk;L^&i7pJ;WSUol!)-j>hoHh?&GbJ4~<4$qNFEMLhXEsFkx43#6k$XTpApTAS>*ucS`s!Lru!BHAN6ZNKh`_6#SGS%ID;e=RIL`)k?eZnaL$!(kodeI|nVsnFZ~Qq^KyUEk`pG?-9%K;Ww44bHXi)&YRe{cS(GTUvE-qsoJApC6SmfYd$U7j1J5$^C4(Ei@D?#VXrdVfo1C|l&4Cwxz)3s1ojzOesNxZr2-8!hFDk}pu+H;>TY;t<moZOWMV*!_#WELS|mZcG$<bxqTYDzek{ZH@OV)xuW`7_U=ZY)lMRq`g(mHvl*<HW8mxG!HYMBXp^lCZ6A`f%##Um-52)K4M5?@z1Tx%tihA1^jr!Ub$P{v0uzkryK^eyc<y6UI?PM_mDKa@wM1@NRg(7W8lPlYBCA4&89o=D1ZzJaoD>246VwbJ(jUll-t0;${4oQI-D9VFHBt5>&x@h`?4ktl>6;{||(7L8<#I!VLuN<2F!D7F(76cbc0e&8L)&iycRC^*m1tg{HME{)czX1XKL;;E<m1K7)6#_0`*h)T_<Y-pt2oSZwN1=U~hukS)++>QC<j0vQYcz*R*FdaXL}YBNh$h2Pk{BVS`_N?L4sG~Imx--+<r){H5cQ-;0=ErOYvP17wpVDRE&lzGN(5%wIo%Bjtrc{$ISKATBaV8}+sWqn>6BxqLpv7H{x!QV3~J}@PiWQBeBd9Ipw6#M--&DQiEJeetQBfHEA{mNOoZdIOxp&d6Zb6nL{FeBLJHCY%_yi{R1X1koLNMq0ovfq*GH^5ieAff0At0nsuOLK95*E6{Zz=DX_6sjd1N^pC!=3Pu&T0f<Yey{5t^+N*BZ?7V`ZUBS#1d_{c@>tD<6mn4{O1(!)T7EIK*sOhT&=%ovT8QBsIO1lmVmirXq2YU#Y9YG8t2iOw-3=3DSk)q}7x|2YK;^m}H~3_?}rqp_*~r?i4Qrogidd8NKQ>p+FatR-^}+o8u}#@CMeG9exbrmQX-VO;SU|>7-BqK&@Dz>3-*>3c4XlfUfu}LeZ;DFlRj-!>bf06~obL4*CVwoFIuPENW%EE0@v;xR{qk&5LPf+df1*{l?$oIsBSva3fd6c0UOFC#3;|IQNcb{qvG~ER@bb>qil&^FXe2VsE0y)Dm1&8D3T*qsAQ}HPR`%qhZbt8qP8{0DBeZGPJa(1W{u;8-^kf7)PS|3`RCkhm6vHiaE{5G@=SXqTR$fDI98$_7Nx#DV1A7;=)s&x>lp%@xpJapjKMtSI(1qX4FPwyI8Po0u;I({qT(N5<=Yjl?9O*-%zs8vI=!oVIHyOwo%yI;bR&T)UK<9GbypZ)U2ZbU2V4fsbx5Fe=7KWj;LydP5Tz4z=UNy9it==y9Y%!ceNHIt%{Mz+6d}N3eB0JY#oq|TGy*f=|*q@(?hdQ*x4%gB~rYEZKtvueKGO~U0)oL@qt1z#7UNBHvPluyfZqRu@-eQp)jusury2~%v32Sz6z3?l><2)^+OY&uaPB^^(3+ws=+1om7Zd~Be`C&uPGr@600iG@nndcJmIG3=++|<>+FeG<4W?SGD%yvXq}2g<t|HW+%f`CT9hvn3z0J-O^%j!Otf||#4OmELFrmqPq()854kh}C<LZ15&H@X`)zU@tSXR7a3ifiAK_i#nb4_R&p<w~4jpmux+P*!Fqf7~H00Zf$~+C>uyXE&YI2mm)wdy-k^)HVwM$(}OoLq0eN!q-#FA=bufZS}G91~bV=3trG9y2mGb#QlIDA?mzzj>uc@8KKv^j@$ij1D{bczB(AX=g~D1c977o&<D$>sC}*PODN1drQ!@W{eXlcppr<F7^`(eC`_jUnbpQv@YFWzHX|vu%_~acOZhN1_0ySG7Yl8WROJw6yZ_@FQuPVGJ^+$V6fvr>isK;$lW1ws<B<+EN;Zt3v(F$Pa0?20d@h;v4a*s+LeBHoXvPY;ZJ6XZ!|J4gmo29l=~H!@pIl>j936iec3x(b<tADl4(12!YP#m)+x30aj2CVsJEq46!Y@-jyO{K<c}+XJk9Rk!?CayGoSjhVu%sByJ`y7Fa1kmdj+bus!w7Li&L{%C4-ajtz_3t4IgCy0J=N0v{dQ*d#S}>)_w34yq23?9gs-&`Bw)MYb~RWd@9!g#4Pq@Df8wD^^oBAEkjNBt70SW}N0Zv9(!Y`g#=6<Sa%;X>n=Z8ul#?DCnlDdN*=klhoTx=Uz+cVU9>2BSfqG9*X6qn<Y?0H|tRq*)5seLzP2G3!a^PlWVPJ!8*pBjL@S2(;+pEe2|3Gq8}C0J*XU>3i^YQPq=}0Nm41PlM=afE|ijyPZLr{7rJD~CD-6W1Swb8uBtUl^N~|bKW10OIJ$RNKLiw{@_7gYp$4ZGfSW78PkJs9_ruyJxiKvl)dl#cti%!o{t0nW%fZ|7>OV>1nNQsz4HoF}gvv87G?bLzk?H}O$BHx&axrtY@DW4DEJly%{in_5X>?J6h%4#YS$dFJP7y9_5pGh-`DMumPCc`#U;&#Ls)56P1^fuJFrnT7JkK$Hfde^7Eht-(rI-#Z2ey-2rcTqq8i}GKyD{cX3t93|hiOHL+h=8j!1L27rywL*)5KifnU%H!qJ?M0$hJTSNXe)pPPr`8&1NT5vS-PH9imVsa2QOodqyN)$nAO#6hh4N6HN~Jr*1?^#9J09qNzK;YnKE$^zl}5lNg7q)uzeozaQX)-A~ILkz(^n1$y$$;=_p6rnzOtATCF<+!=k059fFA*!hQ<T`v5(I>ws*pVET;%~)#f%|CDcAG>8vJ^"
)).decode("utf-8"))

_POS = json.loads(zlib.decompress(base64.b85decode(
    "c-p0xTav^e2t_wE9|FcsucfQ^zm2IO#-Iq2%+IN=wB-Z1SNwePPyYT4Bt>L`Vj4(_s0fNl@Yn+}kqL@P5yW^>GyI2kWYCDr7>(K4fr*XCBr)e^P{)VF4z2H+R)o)}5)+v)<Osxx{P}y5!Rzd(2pyp@b;QQ_eva>3B`M0tlNkBO!hA9JN@C)`_<qi+Bf&8mXRJVQtvKY7SnKodemvcsbwa9UP~|91nN==iY&A=lwXE_5Qx=2gnACW;er9ff;=7(<tpAnAKGWCQPx=)-Czsyk=W7>y3+`?P^Q7uFUUB0(IatK+s{(C*&P&oFv)Raw7p1)LmbixiGYNwDmxgHXhF<cbRwGp!bspb^NX195<>xMPr|9m*_x4qMz@QhsS>Hl}*NrCK65RVDbLA5gD@!9(bx6LLyWo3DU?P*4x#K;3X$ASNZn=T2J73r2_GwRYYM+{%llm@acSPtC9LDYoPiv8G?QYFSDj|NS-_4y~QEN()DobOo+@>0Y%0q*%Mr0B*R~EJ6v-brA+&khP+DWzt`ij>{{PwZlU%tL9huPiEB;KWzKu6*C(z7o5>Tp1?&yMvjfMBNX_>AW;@*M$__t*Sh@Vmr2w?I_mS2y+j1<=eM)c"
)).decode("utf-8"))

_HPOS = json.loads(zlib.decompress(base64.b85decode(
    "c-q}vTXrNjuH2A5NPw?gi;wodjj<&%83BM<CENE-_xx0=i$qjDiB|yp<B!jeKmMp6<<Ec0NB#4&etnidzj-yHfBvI$<a?IVNckGkuMwdU{TdM%X+IcI8j(4YX+(Z7l4(S~MiPzWw?~9V^4CbCk^X~`Oe5)Qq|?aw!ALSAe_ew?Bi9c`@~e@*2FrX1_#ygh<ooexU!UI(QJW+3^<Dq^l&_IKNAeueuOF#%*7u0sBWaFkF!C)gFf!(d!idm_z=+aF{`&iSq<npM&5;Bn^*GYp$Yn<4t&w~jN&kx@@2yz-!BbkXzHd|uMwCX@S|%`}u#!|*N$g055rOrh!g^sx5{!JWONmCZ8)-1oCo+y?7|C;_!^j9m5{#rdGGJuA?U_adM#QZ?>lW%95g1V#Q5Y#SQr;LDG}3=Qa$d3UfjX~VAMpMASmg&;c2)d<)p8%#_pH4_?pf-NUgj?r_(gR`&uV@t_Wio?ITm-06@HP=*U#!Ot3S-zMh5=9u2+K*xz~Mry}t3s)F^vap5GUE$kr^KEBMkU*PM0D|D9&(oTV^}Uyr@YU-RKS%|g{X<`HN3MS*qnqL&?CZ=5yElJG&V{kRtiUQ&2gr&;Y@l0InJ>91CCe4OGHy^wABw7P%5_kI@Isp9NZoK?bE<p;Cm#V>x(%C}~aIV+Q9@v}6TrEkrWw`S$9S?Mqfwbz=3+V9n@ZR<YG%5GM9YnIOcCD4%hejJw`jb`nKcIi~P|F>QfffrzD(R}|edYRU&G+&wodUF{#Tkob&@9tR{evvh;z>6vW*2`8NjjZ!5HKy3f_(GjjNOSF3c4T`4g^V&DiD%_tmdv%=|Ki4NW>x_`B<A(zSp{a{61EHz)Q^K^m8nPetO~PgIBPG2Yu5fIp0!=<P6ksw%xbqGg*skgRtBu|tOOpKkWF-&mC4%K8a0}Qckr5LlJ0L_&q7m}XYIv{4Cep-%Z86gofifl9-gK2aNsO;C_HO<J$u&vyWJ1<o>gAVDsz^aU#$16JznVOgbc*}TZOI!&r&msk4~MAFTwSYV3xQ$km>bC?W}HAhii{|cfAs8){cGQETvg!vMN0E>oLw?lIDq+z`#4r%E7Eev&3mZo+aU|WM<{VEd8k&8GBx@U#ur@<~=!lVeq@^OjP!f{OgFXg@!MsJx(uI+``bz_xok66pXd6Q8O<CY7;dtd8Kdm(KgaAewIJZZshnSvq!bHL#Jhg<+jFXft)x`y@1?s*Kh=KN{cSa?N@e8qfOwx3)nez8i)!8@76`**4jHxn&G-!6mH(Xy}Z6M4bF1E;??Omf$zsWnkBbi`U+7y4v#Cy>6F`^Yn@(lHU|B&bJkV+mdl}BB}bs#rt*#jZ@G4q(_3ymX998^<jU>dtn0~gdX!5q<Rm;!l&c`uclhd8UJ6UF6rOx~bwR0jmcq#Ue<g><c3KL5BBzI}mB4Xo@VAdV_}`P@ddVC2A)9!~Yq<t;EjZ2=x^ru8hGkLcx^(B@DJ(}B&RfWCMSEvVIRQC=Ys7LpW^uic6Ozjyr%o<|vnpVP_qilkxeiv$x&|5IQY#{{!+uJ^y#&F`1aYGdO9IPb9K*{slG~A>ac3CzeNS+lk(}JN;P>1LR_XRmFjpa9C+~%AJ%3&<ALP`@&7i{XYZacCzt>jbSx!K^bZ2woGA0y*|GRSRv=w9bRVUYu*AsIB^>G<~l9Pw~P$}P0!20uYg&bpX)?IftERKqiQxmH~8y0OpA(u3gOD2+)VTsw+tBq%&4V&(`ke4eaLKev>EsO8Ssgdh+oC)L_$q9U-^;#f9GC=M+%B}mJO~$6(8F!Yj8UOd?mh-xgGn3uE1Hn0vOJo(I-M-}n6jMgI-+L*Hm%n!%<VemhY3dwgj7If;DCd_#W;v;mYY*2`iBa`oti|{4Lk{mlHP*SlA-At;r^p*$`wWYxn(#pn!uAc~V@lU+yGz}K=oO-58)-!*Q4XzM%uy9sJQbX~ep@#vhn7n*atbNZPLV$WONr$yk7FlNt(*pOJ2KYqWUiGHaP7}>*PJCLZueSFjU0v&ICGW`a@Ro)^Jn8hZhs@N2wv|IhyMSU!WPn$UOUKVISu5zrKFCBp>H|JKE@cyl?R8sm_!6FV_pu=&pU$ZLi{C=!}Q3QkCfbZxlo`Tzp0R&#7C_FFK30`8+>0OUwMILgX5Xx8pu_WOK>FZei4^kznME*PC%}K+{R$JMnQIz>$jYMTsCssF_VMb_cv*tH_D|c*MnJqeKU@7a?8n4?)$vEqo^%8p7ku3?<4ebWq$L0-XoA}w_Kib!^kBgm*9!G?kjng>m>L6{9gB6UUL0D@+tRkEQR&3{GCZ)dbIx5FU3ot9IZG`n`mHF#8w<Th_PJ0V@+Oe{7tzllv5|CCO>;Us0fs^7TxurlEjehUd!px3f}?#$f|$7?`o{&cjeB3197oQ4U<DwE*mQpV}57V67hY-Wn>H3rLW{NJtNzle@{+KFhFk8;8`vc1?F2>VwHme#U(qre2`lNd^=Z2Zn?JmICqveifJ}-mIY#kujCR11OCBM=xH23Sr8eu-bnf&q2Us_tb!W81T~~WDA_w0xjP{V*gpJfHF_a7QV%F93igLj1T=GG%^@i*VR`DfLX6#|GsWF6omzWc0gII2?~9O{<FR$P8VxMrG?BJda?P{u_cubZ!~s_$LTU%34p!ktTCaR3q-H*^c~1u*Dcr{aE+Zp#_^c3p8n?BPVcGjeT2AYLE55Cm&5%yF)w7T?AYFiT5z=@-T1S?^*1y03zu?JC@Y@OUt}=i7r%20U+!=A5Nd30imfte&zr~#01r{o%m9G1pNq5TRujg|kDIw)~w1`vysXC+%YsW=z@C8<-fVr^mQG&2aonFLxB9QfY-K!2F)rq7I3D>huE8VzPPDUCIN$whpa<6)5z>RwZi$v;t=RH!PGsShhLkd<PAJJ|JJUjM@>#wGqT2Kn2VMv1Q$?8-}bHre@lut~6YCdC%F*57UNJv6D@h4ZzQy)oG;^<7p*!VVj`aY5dNaC)(Cxi*5%r;WwL-}x#C2_T&T*+JIJuos5N!`6Ghv%ldkWx9=?=2u$RU%_Oohf<{o9cr+i|u!gN1v&|aW^U=MG{tl#RQSmB}K<eqzsF$8vg=Qn1lGB0>t+cAX&x;(%Sn2Qo7G5LQ-O!?yGf1iag%UJ>5u^_@V;7O94eToT-_CrScP`4xzsR%X)@LdqsBY9g9}OazMXy5N8&VBtY6^z(UL*1-6KoQm;lxi<VYze+adJ%xjiIq<+)?emT$SB%z_wDi8inIe1PA6`BRCtP@g!3QG-YVVYS?^yoP$Ac>=beIpIWQ;0k#Ie1PD{GH2Pr^s_!5k~7dbwb(}jUGLx3_cTjPUH4vHd2N#iuauIv?Q(PG{AGZAWWB!o>Qin>HZwxIbE=<XRzZFc}|&prVhuH0VzQeQXJBlNW*weGLg2wbHUQEvJV3iWQ;TbsT!m~NXa2xgtR>;TtIXpWl#r*BnKopA_-JYrQ7FN@%?K)ndA0%)FG9Lv<)0a%HTOI>C5=C9j@%4darbQFX{fZ@3mlnztfF!t%S6bpB4PzdLwo4J)5a3YlKt)sRKi2A+`HxF$1=cI+&4&)BtHrqzb+#W*5H|PX_}68AcU&*PW`)yIFx2VW5%WzS+<P!i)WX*K_Iz&#6Chs3Xtmgfw0tdC#etnD{2AKlwW?<d0xVR{zhCxSJ4r0r;TWtOuUm2omO8qGCO#s4h*z+zlc{o>L`uOfgxhGg8F#@jM&MZ<Rx?#}f!D@LDiEkBsjY+&jdUBNF;J8s=m;!zaPniSeJs72%-gw0Xvx?1#J}Js^qmoXX8J+Lh}9`6VSbIkMsL4rW&ah)6<6=-pU8RD`6^eTI=Xr4o-xfVNmeqzr-J42l+&E{4Styn~6(ZnvsXFt-xiP2>y>VA!{ygHD1R83y2VB5kwynv5evYH*zrWa(D0Fu^f3NF{6^yZ;WJlkaZxZq5lM^nkRzsB_K<d(%XWpax|%6&AkklDeIc$^%k%NL)fRz{iQMQ@@WD{h-Ai!A19i{0{g1Q9vrUr_jI;%B1EHsZ&26y=`Aas)STskDCO3SEl<lz!&I%G$0dHsJ&7*opn%Rc{&}=Zn$1KjgYWFr~tQRGkX@&<&ZE_grSXkdqo?m9gxIjWd?Ad>g^TnJWd5R|3x{aZRs*na!6KrE+mECJq7YR*mR`c{uLwDA0P=J3FLP;l5x4-L<P>G6B1^xtl4o!l8J;~R(U`|zmTuE5>oylk~kz^5{7v}HuNuQeTG5s3lt+JFf3Asyz0(#q33i$8m2`7Bjt_s>v>LIIn{$lRe@d^`#aUx#)TH(;<)u5X*iX_NbQh8>aJ(ia4p!%3nT$Grx4b|CA(38Q}0EsJ0uN|t{)>QAc;dt&K%IWG&Fa`w{l{nK}bl_RioN4Ya}L!fXCE~380{mxS|7<mK=~8g*F9{#Ffd7;5zB8<{AVfmrdH8uj-YSN2-LBZ}rD4HvuFCuGmFqfm9BQlnJSWs!<{sH@LC`e1rjPE^NZo07-~)T+KVRkh(z{VAd64rY$5~dm7N0J9OYJrWS&chC^Dk>jcM?OtvY*6K0Xr7|9E%K^r|a%sEEtgd{*&Pw)mOlWoFU==^|$l^_+)PM}$mK+Y~xM^YOtSx5ysDBELdH<kW3@tmTZQ+ZS=Cw`yLIdSvA6VkKi)B~h`Nc6vh#AnwjSh%xS`EWgi6oKW~y+XpX5L(tflDaC|M5-6#_$~DEgpf*rq#;ss^acS{W06|eDiXaVMj8PjVk32W8r3Z8dO)((xE-=+6}ruJmpI;Prx~Ozae<$VzF9jU^`IASnwc{-Im`qS%rCttGqRtjG&5%f>W;UEImib)A;}R*4HA397jy$EMEAI;+3{A4!_XKSAz>dN0srrW)F2Gkz&GR0K&Y&-<#LB?XoZ|3dN157NI)@mhr|&JY$kEJ?m+^Iu>t3>L;kc8(l%o*>Zy*35zk@(Qity&r2Ol9PF$o{4~2zMFwUzp3B!8j1(m!}V8kOe<0%YBW2mO`w+7{fuaH{M0Vh*H5?|0}ys{ps6pu6xYOXlnB2rFB0KZ)AbS64&G5$^s$}ImbQVEcn;jmS(zBN#oUO9DAPA8=Lpqv^NbtY1b8!17#Bj3B>j2-Ve6=)5XfJ6`>sYA*yko=Q5ZZB$wi6!)t3oOP0>^hIM!^GJ=;|fUqM#}UC4`>uuoae;Ur3?j@RwdU5B%22pC@B@{AXRR9L!-bKdrs)1Whl82qk0?oixx=^NEMK<^<r~K*znw+-O4kG2}HNKo*`0$&~PKaF+=+mp$=ASbAXOY{8wk|Y3MnfJStnv*dCBd;3+&Kl|!b;H;P67$QEYyM<h#7&moeUY!s)$n_<^gm$_-C9?T=5a?0j)L$9Wre%;;0xD`}NHVfw7mB*4agpkA`iK%l+!02lMk_Jc}a!zWHE?T}Tgy|GQN0pGaEsg$>MG`=2uA8?<5<rsR-VJlz(Q{IVlqXUS8ng`fw4M_qZB-K^S+-sSKd2m$5-0-92(9WbJUgthLZmA|Dh4SzB&^0kq)i-nLc+6agd_&ZlA|nA2c%9&m^Vu<fl(aNfSg??-e)-?DO77+&^4<#zc9glyojo?+bgat)%9sN=^2jqspdM>UspMmm*G1-v}B2!zxX<${x;I7*<W?et_Iud_^#~{m(Du78gx^YL(lf=HZ>^lKx$AS#5^rEwmb6@FJrfk2c%+-$)|GLaf2asjdYY+`Jt^kLjPF|FA<jj%NIi*!h7gBK<bY2inS<0^jnM6f<CP3`k3Mppzi6-)KrnFIvG4QF(EW@?IN*U+lH<)oDpUcIv^>8)|9Bzh?Jm^Ta4<>#GVz0By@Hsqy}n9On#@E?*D3#Fn5!vIgmmw1zDE~c0o`=!rovNlx{IunQD-B7u7*XJGzpH%lQsccSsqKDj}hNgh&M#fmk9d;5jwO7bbZA3bFMn1pg8!MgecG6H=nan!ib%(}}J3^E#(?VDaf&Y(4Ce#mB0Kg;Y$Z2OA(P&@16|))~H6$~H9e|7;-0U#Dz(cv<_j5E6F%YG(1zcV8~Mk6fkm#?BJ;w(L7SoE2)dYG9vMa~#;g3wvRxtF3B5PYyh?<!5wQ_&QYBSIUxo!mdiy9oe{1v4cf{^O685!8Kr{3SAI7bx_-(-$LCO8r-!4Y^ZvBlK6}$TnBzz77`LmI`CN)s04ULtMgSe^ad-C%@xWc?rV)m-DGGzQguX$T@j~nj)RaCx~LU*1o-qO(}B*i&{h-$4U%ezHx-cZ8Nb4}rJHvbgT8G_Z?&H2?3#P;l#no2S%DwRVQO2*Q>d=9n#|*XcRGV--vVB8aTTJOkP7tR%j8%6qV0=H7>uh&DtY8NsmtkLM}iveJMe@g2PEqSv~XXjoeF<O8m{v}F&sKX%BB*$(v}~^bs%F7oki-@Wc&#UTZpTnw8qC&4@j8FkN}CFg6!&xEK+%iRLt4ELdw)3BD<$9f&EuZZ!>{KP-vq#C3~|Pqz3(Y8L0tMcAnE(Hn%<A0g1U|XC!?<k^rd#Pirm2h|~=d`a})9ln5yWNZC}RW!IT)laejcATo0{6=~^+By;1S`pJ7w7f_p(wq!)49nZ)HNga}gNUJwp0VE});*fkNjRbkbdI#_Fy$w?{xn3;W(4deP4Yo1=_QzD9aM{K|xX_?byVKvc&WW4E)E8kr%cAn0Q+17No*KK`j(FAOcUlnED*<)AIBJE2<(C}RQ%A|xpkhkHM({sD63W@xR-lX|hbHvx$4L2rgk39IST1Wfqf9|_A#B;%j5?^tQtWhS&NKjNxRm=7l5K~DNSAA}6d5}ycq22gzc!NZg`(7PB!R`<9+4^$3b@zFMv}u;3kiHxMr!1b?>-?&T`#mdZa3W+lxq1JA$6cJ<S@(EDPN389TdSUBz!V6m|ln^gk-l3D6WhGDc6ON^1R|5%z+HF?P9WPjD&q9*Jjq^6L)}Taz~<Pf0yeP>IS)xu20-?o*P3YYOJ+49te<rMdj39hV^)prwXkMJyLUVckYoUu56UsAzDKBspA|jS3)eK{)ki^$+=J>vJ$JwwrFfeA2FL{Jrn<pkuEr+CnV3w(>IX>I(Dg{R_x5pC+u%LK0j#3y9h}P-J_evultqey@JuBN=AX%R!|s^$2LmxCekiOK%@$RKrwu#)om?@d9eHvNnaxE<HNi~b!WG;HA+Z!f5U8c#;cH-!n1pglnhcaWvUU9m_B=zwo&hdluf3Hk<=j-hg1S2h2(zv^c&m%3@O1C!u)OuHk==j*};5LAtbvyIcAD7AvLJ=!c38G_FAEH1S4G#1sISm<Az-7JYdel{>F7qr{<>b)j5>|y+I$5+M(@DL~jsRgxi8*+h-(o1-a^w>T%054I9=nQV;wZOQG<phN&3hklJILCv^nc2q{B#QiSBI=lPyuu`(j%2c)=BtS`c~Nd9@!py^dq7;J;8zQ{p?svt({t|hU5I*Lh0H}ZEPBr#QOzNaPEv2b~KKa@*!SAbqk89=5d6YF<;um0{b&qCc%m|9^aIw9F!oeJg9*=)<!%vm5IzPs{}btf|T7B%P=BPQ%PoB_U`4n%6fhRp&U40r8X3v%ph_eZ?q#hqP-DkL?*eT9~@8%YiS5Y@0wBuo<sG)qdqrsw4Ami}3Xh;l6btS?!77O97<JVuhoBHTum81|9kE)8P(I`nY2pmDUUKf>M4JLN}E^$x=eD~>YmY46RDG>UtrkyKqj<K1^!P*a3;OJZ1Ai1ezUU=R}KZY&aZ30D*7L!{=AG7yRpDVyA3dlN|^&xFC4&5~=TyT=JhOvZ|9^103lm3RivDFIS4-LKC`E76{f2bT#+KJ9*)e0KUaQZ@miZYrh}!guK<67O;OjD$Y308)b1O&NCCY(Zt&06(e0-tirfl0&Mdvdki(A3q#YIwA=niRpNcTLtnl;kMQntz0Q|0WP?wiLN*V=Kn3_R3W&=uXlZ{HL9Pu<54-#6+ANziN?GW(q1atf$XprGI2IyqYmVIsXQaK(C-r3O%j)-cGxpiT{9glgx#g5dkJXtd&P7gk2**615$PL=K>N@=ZFscC_KALs;#&#cxt+;WkN!m8K0O4NnGX2?ijA*VK#@Pw5&fN6{1LYIy*HSMh;OGIJ@DV@lI!?rVJDVOWp1N#QTHc*<~nfOoW8_u}+lr9g;=6JA;Z!bVfEmmhZiXb_-eb<Fac^+RQHYo6mLu!KOlxiIGrY3J@ZY33^S%v5~NJS_lcvfn?T*g@hF8K^eRq6g(l70I35Vy+9sEX;VJji0^%*`iRtzNQ2Jqgd}evWtV;Z8%Ur30d;Ai0s"
)).decode("utf-8"))

MAX_MARKET_ORDERS = 10
CASH_FLOOR = 100                # Never let a recorded PURCHASE take us to $0. Hands
                                # vanish nightly and are re-hired each morning, so a
                                # zero balance at end of day means ZERO crew tomorrow,
                                # and with no crew the route's PLANT/WATER/HARVEST steps
                                # do nothing and the farm collapses. Measured: the raw
                                # trace hit $0 on days 5 and 8, lost the whole crew on
                                # days 6 and 9, and fell from 43 standing tiles to 2.
                                # The source route never dropped below $75, and hiring a
                                # 9-hand crew costs only ~$88 of Fibonacci, so the floor
                                # must be small: at 260 it starved the route's own seed
                                # buying and standing tiles halved.
TERMINAL_SWEEP_STEP = 716
TERMINAL_SWEEP_ALL_STEP = 718
TERMINAL_SWEEP_ORDER = ("CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
                        "STRAWBERRY", "TOMATO", "WHEAT", "WOOL")


def _sell_priority(item, qty, inv_map, shops):
    """Rank a SELL by the price damage it takes if it waits (EXPERIMENTS #51)."""
    inv = inv_map.get(item, 10000)
    now = predicted_price(item, inv)
    later = predicted_price(item, inv + qty)
    impact = qty * max(0, now - later)
    if impact <= 0:
        return 0.0
    demand = max(0.25, daily_demand(item, shops))
    excess = max(0, inv + qty - 10000)
    return impact * (1.0 + 0.25 * min(1.0, (excess / demand) / 10.0))


def _step_toward(here, want):
    if here[0] < want[0]:
        return ["EAST"]
    if here[0] > want[0]:
        return ["WEST"]
    if here[1] < want[1]:
        return ["SOUTH"]
    return ["NORTH"]


def _align_hands(recorded, live_positions, want_positions):
    """Align the recorded crew to ours, and resync each hand that has drifted.

    Hands do most of the work -- up to twelve of them against one farmer -- and they
    drift for the same reason the farmer does: a blocked action on a weeded tile
    leaves them a square off the route, after which every position-relative step
    lands on the wrong tile. Any hand not standing where the recording stood walks
    back instead of firing a misaligned action.
    """
    hands = list(recorded or [])
    out = []
    for i, here in enumerate(live_positions):
        act = hands[i] if i < len(hands) else ["PASS"]
        if i < len(want_positions) and list(here) != list(want_positions[i]):
            act = _step_toward(list(here), list(want_positions[i]))
        out.append(act)
    return out


def agent(obs):
    step = int(obs.get("step", obs["day"] * 24 + obs["hour"]))
    me = obs["farms"][obs["player"]]
    private = obs["private"]
    shed = private.get("shed", {}) or {}
    inv_map = obs["market"]["inventory"]
    shops = (obs.get("town") or {}).get("unlocked_shops", [])

    rec = _ROUTE[step] if step < len(_ROUTE) else {}
    farmer = list(rec.get("farmer") or ["PASS"])

    # RESYNC. Weeds spawn on different tiles every seed, so a scheduled PLANT can
    # fail and leave the farmer one square off the route. From then on every
    # position-relative action lands on the wrong tile and the farm collapses
    # (measured: 43 standing tiles -> 8, reward 5,027). If we are not standing
    # where the recording stood, spend the turn walking back instead of firing a
    # misaligned action.
    if step < len(_POS):
        want = _POS[step]
        here = list(me.get("farmer") or want)
        if here != want:
            if here[0] < want[0]:
                farmer = ["EAST"]
            elif here[0] > want[0]:
                farmer = ["WEST"]
            elif here[1] < want[1]:
                farmer = ["SOUTH"]
            else:
                farmer = ["NORTH"]
    hands = _align_hands(rec.get("hands"), list(me.get("hands") or []),
                         _HPOS[step] if step < len(_HPOS) else [])

    sells, others = [], []
    for o in (rec.get("market") or []):
        if not o:
            continue
        if o[0] == "SELL" and len(o) > 2:
            n = min(int(o[2]), shed.get(o[1], 0))
            if n > 0:
                sells.append([o[0], o[1], n])
        elif o[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "BUY_LAND"):
            others.append(list(o))
        else:
            others.append(list(o))

    sells.sort(key=lambda o: -_sell_priority(o[1], o[2], inv_map, shops))
    # Cash guard: HIRE is free at order time but everything else spends. Keep a floor
    # so tomorrow's crew can be hired; drop the recorded purchases that would break it.
    spendable = max(0, me["money"] - CASH_FLOOR)
    kept = []
    for o in others:
        if o[0] == "BUY_SEED":
            cost = _SEED_COST.get(o[1], 0) * int(o[2] if len(o) > 2 else 1)
        elif o[0] == "BUY_ANIMAL":
            cost = _ANIMAL_COST.get(o[1], 0) * int(o[2] if len(o) > 2 else 1)
        elif o[0] == "BUY_PRODUCT":
            cost = predicted_price(o[1], inv_map.get(o[1], 10000)) * int(o[2] if len(o) > 2 else 1)
        elif o[0] == "BUY_LAND":
            cost = 0            # land is the whole point of this route; never drop it
        else:
            cost = 0
        if cost > spendable:
            continue
        spendable -= cost
        kept.append(o)
    market = (kept + sells)[:MAX_MARKET_ORDERS]

    if step >= TERMINAL_SWEEP_STEP:
        planned = {}
        for o in market:
            if o and o[0] == "SELL":
                planned[o[1]] = planned.get(o[1], 0) + int(o[2])
        for item in TERMINAL_SWEEP_ORDER:
            if len(market) >= MAX_MARKET_ORDERS:
                break
            held = shed.get(item, 0)
            extra = (held if step >= TERMINAL_SWEEP_ALL_STEP
                     else held - planned.get(item, 0))
            if extra > 0:
                market.append(["SELL", item, extra])

    return {"farmer": farmer, "hands": hands, "market": market}
