"""BL-MDgogo-10C4S-R0: public-replay consensus route with generic execution guards.

=============================================================================
ATTRIBUTION -- THIS AGENT IS NOT OUR OWN WORK.

Source: the public Kaggle notebook "3094 score | Kaggriculture" by Salem Ali
        (kaggle.com/code/salemali7/3094-score-kaggriculture), published for the
        Kaggriculture competition and shared for forking.

The notebook describes itself as a behavioural reconstruction of a high-scoring
submission, built by taking the majority action at each decision step across
twelve public replay traces. The embedded 719-step route and all execution
guards below are that author's work, reproduced unmodified. We decoded the
notebook's base64 payload; we did not write the strategy.

It is entered here because our own agents cannot make a third quadrant pay
(twelve controlled experiments, EXPERIMENTS #48-#56) while this route can.
Our own line is v45 (main.py) and remains developed separately.
=============================================================================

This is a behavioral reconstruction from twelve public traces, not either
team's hidden source policy. Clone preemption is disabled in this experiment.
"""
import base64
import copy
import json
import math
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rM%U2hyoa{MoP<^yLqGbH_{mFB#{X_pIqcyL}2iv@g!0pt9z_M74VZb{_ybazHZL}oYl*6@=Ea@12@l~t7)85#NWf4}<IUw`}CUw?b`4?n;9>Gj8tuO6>n{oAkq@h|`R<riOm{M)a;{rg}4>&wqSzxwX;Uw--N!^7LpZ$7=cdUg8#`1;Ggo14eS|G64J<j02(pT5tZ^6~io{pG*kJzo9%>ic&ej<4JwzK-JckMDkX{q-qt9!{^Ww&B+wzds&-8vWtp@%Z-gox9nue>lE>`0?wfXD@O(e*83kk1zA{?#-V+|8)M|&DZBVf9UesqhHNG&L(1`zy0zJ!-Jn+bTb{m<)`mHzkC1omoLlu>GRj=GuCtaZAGSId-@$-{`s(fdjI;zPnSvEOx|ENobj6s&%2T@`sFL$9J5))FSQ3RwZ~=<7vlA&<A<3YOh<st0KVFr*X}ytAxk59`hqJs*I{W!<9_<V8Q2yKY-`RXwT{cad7j?!qMuhGZZv1i*I>-o{q?^L;ZI-x?_?t5ye}Q*Y&^%;;aCC-JJ<o8)$l)^6Mq*+xpB|bIQV>FC)4}%ss8Y0<9MDPWPM;5v&md-6!ZHQFXiY+dH(D8L>aGdc`fhbDDUy5xoKaTmj#9g5L$kFu@7<l2Xk8kOB~KZFsATRcXTgc0_cB)&&Bah7kK;P3mkqL52>>{&mS7^fp4=(o|{kictVE<v)P{fPJQnhv-UKq+RHut22R@Wx6Y(Z|1X`DwZ36AVe5`O`GGw)x^_vlBO@AZC&#&w$M^znaut>(9xAv8!HG9}`13tIdiHR0qa*a`kK}prdM1AD<+;(jo<H~D{rlsaPrv->_~FyL_wW9B?%2V<Q|Au-kJ7nzcFRT&m|yH?yZrd@Io>?a_e=Qi@J0&3`tu`&BXs^$HrfRv+JO)O&4;l_!})L-F7nq(!`tfnda%rL=qDe2x!^9>!Gf#q?T3e-rgy-wOP8FaqxW9pU|#v0kK5=EG`K(Z)UE3({C^r;$ER5LX|oe(r|{Tt9J*NSG>QlaRrCyqLlci{KWz8>mH@9j7Ci)j4pbZ^;DymA>PRV0FbP_%F~&&_<0(dSYEnUT!cacxGoyR6FkE7@V6he%EgGMEo|;WISo!k6BOLit(GU6l^@o2_BaRa~tPof#3SG##MS~s2xQex2zG31QhwxYLG=_%uOc#02J9XR)YXH|0UJ*N-ii?2%JY&X3(lY{ZsG=R_TL5|>gQ+z#GfNopk+OhK+CT9c4D)$WC*-CNlN7y<5{%-X<c>3A-4NOhDLFcYyU2EL&`<NPUcQBT9*TECg9EhV{P1CquNLF!_SJ$$57R##C>>vn@gQ>Uc6RuZ0rR9rZSBESk%=rVKJrK5>={S3SbN|JasQ&_%Q43*eDTsp1DvDh!rUZ>RQx99M?+8M#`I()bbN*ZFN>BNPx19P(*H#E9=(zz+V{bC==x3(nPLiJ=IUHQl9m4zYL$j34OplJvp2l1&U4K~+l+fOd#8d!wqN9sAwO*T>o4>4;Q^%`et%TxC0wM`6RYnzur)wlK~tZeC;sE753f((9Y1{d3;3=$`IpUS6CTR`D|nrfU*_JP;BwGUXJkt_{fl5ZbmKa%7MWDwid2yl7ga*82v5n?+z8-@&TYpbU{$Psu#|9(E{2{ize~UsZ}hhJF{ZBIys}^hIj0o~uTzg~oi#)L!YcQ+_q?^1YuRf65&?PMg83(3H26;iI0#tez7IBWToSz8ReD9<JpQgY*nZ7q9I9_<qhZtu)SELV9oKg30IkS-m$|=k<@-za*}D)j17v=DtuFkYs%uhsbaBB}^#7218SbP`Mn<xY)*`rKOcCIVm4ri%B3!6H&;G!453oPb_v8dCXTPynh=97zfr1{5*B6CEg&eJ!k^=9buYd4t;L3uWr(-yv+GSpZ!Azr;X(i=L$d}Fy@>qW>xvyL69=A0ET<7$!ZdyL~`YdjGUf>p7EA&k{Baypk;4Ih{9I@zu7T)=Vh~aaCW<JR6s5+#@zJgwvLG#`Vw+yYL`R$kO4{sXEHzyFP?=gaH5-Z_KU#Wct_|nPo0^Ff>22miEBf@e%1`h|MaKU*br-z3xpWSQ|w?}%r)+m`vav8wW3H0SYdHX7_9+y)*tR^_yy+j+z(YSsRD2_&EuL}$=m<=kojxW+pEU~hgbol|WD~R?i!#tbNCQ*|>*rGy3xX!5VayGE}(|N2l_QzmFI4QJdr%%C3!*^7xdSbOgl{B~{HzH3Z!#@RHZ6%jL@>>;0d^~Z|`xOV10je2jVxF}g{{V`v0^02kSMPEJSm+gIM1)EfhV1U~fgTbtc)7ujw-_1KrM`Jw4x@mP)z}@0)WmG5AmJwZgJn#_sEDnFU@!m%^N<y;th2Hkt6m-Pb!Z@!74H;^9M{0?Uv5ErgDEa%yDE8k)VZXP*>~j37{nX^{0{$@r0lx%O9{bQ>{kBMaEZ-arlrt*eD3hWa6Qc~=QS{W@+Fra@C8Goig+>#5}=);X$~v-HOuAWKe(~_)=)cAPUF1X8gn24t*?_3OW#=4s3R$)@QLVrx)XU*xkRa?6pRr9A{2NYm1(8Ht+FW`BVLST?xyA;H%}Fbtw`U2f(GDYtTt#-;%aoGr}i&XLgqDse7l>+^>7UxbPn_R_T4{P&N&2v(05Zs9yEI)y}1w=09!U3CnGsPx}E^h?4m)@&jhSFr`R(0fAw(^2SF23NWcj=zU!<Tn;^iNf<gZ(g>*5<Y{3dM=({!q{Yo$J;=M5Ng@hB>%l$sGQZ~B{ve@o=YP(aHZ%JGSlU<<Dvk2Vpd-+C2ABIc_rrgPWK2J~Sd=>og?){&?2>|kVDttVuSv5%cPfy!y(`h40L#7Xv>NH#-Yanq}mTapH5#0N1gi?RZl46S9<Hh%#CDOLp-ID16_pY|#<*~_M#%ZV8=zl3qpoj}pd_n)XRF$kZ+ZASD5VS?9Hw@x0sCi&2nvUG9UbBnmr1uof{^mhDi$s(mqqRU=&dFXAYL}tsf^m|;0Z`j(Q4ku(iOYo|gn|>pEHqe>YORDPbHlqzilK(FO8aCItzdyK13-Kl8CBUr@SDd%<#qIBMt1KXSGHM}wm7FuXEYPIT}1h#e;y*(O{C8Ggej3nPx6PW>1GKx<cs+SjFV$yr2{l!*)hIOy|fv|f^H2?B2s=md!9cRdC~W5acof92wccik}&<^A+$=j#_?hzQ2+aA3bnJEu;vMzTtyCUcEHW!rcINI%h**Xq6ouUvvlHRKoohM6Tk?S7pt<^buv%P&|QuBCD~Nun6VN}!>HWpEac1FRC20g(X2J2We~syAu>E&GvKeP>0G9oO>*VP@ruPu#K&2#VIIG(z_Bjs+_^L67hX~Ou(M-@QaP_2G9HukQ!7lFS4(MGSyKnLZfK*R2(K=MIBXuj>*HKmQGreBU@b^!YaUQRN7Nw1aB2JpRswuEtC2PGZrXO4*oL9+p~{6jlxZ*xJ{x*jQL(>~7|c)&OIL`FeZMA8x5HCWs-hSSn-1ui!hyQ9*sU}W!bn=(F10WN?<9UjD|MS84X)(kLXkmKnHs&&$<iQ&5l%F4WFw{zER3?6a_@-=h$QeTk?^{$i^vcB4v-2;<E6T*l*wvcUANt<6XP4V>b}B3a>F^=WU<rH0OAbhu;|BV9HaOH-h_H!tj&*8P&*?c)M}bDg%C6>{CB1+B6?~S-SB<IfwkS8i1LU6!D=ew%*=Rd%6Cx1<pTqsi|jlhC4HfH3`25foaF?;(Bcm$M<}@J<5A8Qh`&`~?C86=I&MsH!f`@E(>&wHUgJ_@u2%<Bs=)A0PRbU~1v%{bih3_8={#W1!(#J5>A<f;`+|@E3%E{(8K5{Oepl!Y<_mq5f%Y9z-6m&ahu7xSNVsdfs$^kQ54npOQ7`M5Z6#7RS*OCn@uau&Vc~ABmLbrZt_C{`H~gjC#Z;z)B3;zCgUYdCTQcYtQXKi_E29O#9BE#@D*PZT#-=mU(tN=?9Dp9^Kg8FF4uL|38axP!Q-Y3_VB{p1Nk`6e(>)bt1TzL(kAFg?2u*PVN>30P0*n=?j9}JOG`TR0S|uz@M#_Kq_T+z!BnJ?HlAGeJb-#0>_8Rgt?8!F|=cWZV!=_8+vXsn}Z?w5t8Bt0d^u0^Fh(<UOfx<Y_CimnRgLoBK&GHTR!fT2XGJXMCaT*ds-Fi-$pDT*TWHs(d@=F#kvUgup7D_lS73wI<649|A?F{r)UDgQ|y3~r>3qBGrlJ*6Ah)a2>Oah2%_;9dO9Q+txdDk-1Wh)I{GHyM?ej`ttw|%9JoE8i|Za$h8<OJ8A*4zs%OMBmmatdQ{X-(Fm)03gaC5bMxMIa*mcTdokz!EEsCwHFcea8}5rPFdj!93e}tt;C~*)LhQw)~3-k0}zulj~@ISwy03$<nO;M@>x_hd#CDsu4+Z06H*kaiRConwp<PCmlBa31eiuTAF7~d*Cdwt>UKfNIQnA%ZsXkxJ7ny!x$xRuIzEkv`})18ka-zvD<#k;kSEplT(8OmkVIwAWzSy2+Hj30^5qNbF3q%bZOv~l4|rm-l$a2%z`)S&~#M#8{HtvtgTCf(X=FO&6ZJ5wGB6a2bNc%Ns)=#Ezq9dZjClollqYZ15an;-P#HhiUC9rh?@jVJ&b-o8hZMF&!5pf@X)GE@tvCjbtPvhETBk72j+4n+GSdq?#fN9DmqlV2nBGC)v-;#>&E6fO4Ba694w*S8BVk;S|URcmR4i4^^J%h@s&b2+$6-Y8oZ`($C)?xwqF6G;yzjjz_0sdWrYx?3$sd@>C2kGvPiPi$IogUE7rBqv)-g_#P;cC*Wqr7lQc+L@MMPa-5`ooxzc*jIM<j#(CKUoW<lNv-())rIrDD&zr|gSd8cJ-(6w#?jT5q3@ixz1t~RTz7!OTkjFHXoU$$MX)VNZm9kas7ILFI<wdE#ax*2SZms=c*j;ZRY(W#NtI4u+tefbW`x4&O7Y}NpkTk;7W3r=BUGE1WWIo+wdTm7z#O70YTrGa!^wZ2|q3)}_Ig)9$tvqEzmDmGTod05m5nP<Walnq|$XZsX|UQVu{B$Xs7bgO0v0s3Mn+{s)=o0*h31(l|iaqH4vR2UOqt>ajegJX|_CTUHJEl_A!;?eZe3hkXKZHv>GSq_nk7B|~aEtV-z9A}hpKe|MB7MnF+!|7_cin59?31A~?=uqPU8Mo-8?I#mDK2z`EhknYnToOw7AW;1JdIg4_Ij<jMOF-0#f=loo!>VDzohe})mo<$f7RLn1`BlmIPqd|RqLbLPM!p&1exi<Pr@vE+ZNyI>Q_YE_RrimDaiero+I2HI2rF~=48_{zB{WJOaNYb<PMAJ+)OV%k6!(9J3^t6$QQ8hBN>PrO#~UgGeAm%f!I8s}6||ptTB)F+N5BD)YGwTdtvs96|Kjek5R}18HsGtmY{&fl_$gIaUACb>Y>OiD>A;F2ITfz+=O@b}vmye-fTtRg8Le=dpx-B^%Cvx@RcMEd87N5=n^}=CHiPMqtXz}z+%`aoFV<;~tOKLPNK!2n*m++-t_Wv=dX{`ho#3EkiY`k|4`dw^l-2i&m76IpEvHI*rbt=2f=B7JOl+Db1v4S4NlVz)15+#+aSCH{@Qr9woEQ4=xX6?%+7X?|+=JYoE{RPf7H$rYl_vHy4<KZ;67w<A%~yB_cB_4;kSOzI-ECP)$>u&cK#PLOt36p^Z?ami0+Lj~aY^qrX3a@t;PZ|6wF-h}%1_X7RbM+|_0FF2GnO3}*DoH$L#Sb2$i)j*I^$Qez<O(BE=7WVuixI2FNJe-V}YW|%PEAjcaJT90x15N>j~eW!Y*ZT7=&4vh*cz=kK0h>$BEotUcaV_$KeZ33z~BF&fDsn?n}<{7(>6jcdh+}^$KPM8-4|%WCAP%_!k^R7W<%2amAKIkTJF^(0C0E`8DEvg;J;t8`f-@R}`J8w7DNtYZ3?8Qza8O`3>IWbg2%6RA8v@D5tdnB1GhjoawsFi|jtNw#|;_acm9Ba)m~*ld>#G==edqQhzr1L@xIm?8|<gMPgob9(gZqO5iA~ORyk$bN9F~nj@klR0F9%2=D_mN~fSmIY}=tuqOdS5|dC-cP%o8`*{4zya;)fHWw@~qFi8>o`A^D3MFl#IXaMq=21MmM(Gap#XT4U6pUA-Au5UdMziyy={6-Yqx8gE)(VytK`7bGngYO5_(Z_~>tZOx&9tlcdFVt56Gk)Jv2w*-CNg?muXpe#0*-c*z8np8czWIxc4|`LS>KmJ0)n*KDCFRUMmotWLRc=!qj(~8m02rb2!8K%g~KePHBb@~&drh5W4((c?ksWpQWq_Hn$x&vDJvlB#6g^QDRGn6PB_W(nor#7_*y9DDZ^(ZO56wW5^p&q074xjg`=E==Q$nl?y<5az>cF1|LDToB@Pzl%E_JyTWgjXAYwAladIx<XV<_mKX9ULM3=NhuHJ5(n;s#uEdQNh+$O3{n`877<D6mwlz+V%D{AR{hx&100xt<`7v-0))6N<CWV|U55jq%dqrqtLq=}8zr{`K>O$Z^uRCSOzNnPj;9M-dTIcTs<HJf$nvI<8^00WiO<ZcNmo~tlMfUk|g-xUBcS^8-Su0T`XY_pTpNZ6ZdNOZ4LAD{4&pJB@#1vPg?SHWzmT>nXS6SBIM1Qx^}q0EF)-(%s)tgdE(RKx^7*e&YrYq4U4UZN&n_n2@-<Mu)`Uy#XcaJx~7bU5@yGbZ9vx$;5VMUnuP)5GtXdI9SS=$8-9aPDd${ls46*}876wTPHo7A1^-7I6agN7f`_Pqc<DN~ae(FNF9M2FI$?Mb()0QL1{dqxwLje;UV6U{BvU9x-CHOzo(pgugUZ#+ZX8=~HTAPW;(c`n0Nj1uY}JKx*|o6&D&#4n9|u{lAQK4XrA$Q0%I-hO>8fZ7K{SO_`GQf(cmJc;r}TMI0GFDdJvL%28i1RHoa6T5;Zb!h}K+7#6$&KGG<8qCnx5jayn7h<Ttnj+PISdP7t@L@AyO)m>H^BQVC{nWARk5cgW&ILOnrO&)Oz!gNAaBO}-SBAY0e8I?4_bgPSJl!y;{lS(z;(!VUXhLFM4Opap}h0JwPk9k?(-BOLrLR}8R$Wo-lJfuYvSUnBX(w7WQi3&&T@<|#8>{Qy#DrrxqOvl~V6*b>un(|TtDh%OdF{4Z@zJx>)ySJ?I7erTNp0Q9tZ0e%Pr%&f$IoSq(A&_UwlUv}fE=;l|MTTxpKan=|jaAtlFEH?>%J3W$LuLmQx0>ahJAA3_m$2`QvNSB)3SHL##+w0p5K+^-0G@BEw_0-BFOnTZL-j&|2c-wds6ScAj?Uy1cg<V03Ur?*y=_+LN=+Ah0vT=TLor{qS{}V6156Jk(cn_O5$Dlm^h8ckNKckIi^tz-oPI=^zJ<+IqhD_II+0DM)O~3q3GkXKJz@2QUi(^OeW7UgbPh8wYJ7646D&miW_n{uhk1ogJrs}1u3%Ttm<#IiBfX_Wi>jE64oymzDPufAY17CkcX%|*TLI;Rq~2fEuXXy}@OSgGkf>lOw15Tp6BVZc4PXqV-WmYrzmHdGHT-Ho#N;K3;ix|fPPW+=fU-~)=AvZ`U$E3{_fn^J`c`|6q3sqCs9d6v#Y_sJOw2{WUDQO&Zd<Px(K7ZSR_Dwh504&X4Or)>9fb{_kYm1#*DNLx)L6s>=h>hF5JefJtxATRB*dib1W?e;-vb|(2h-e#arN%H?|>5a*nHyd<gVayZM?<pV5zAgDweO6S1T-Zt6540hFice=tXXhLJ(i!!527I3~cf^{sa`P<{)OM2Z?5x-25W)zeM+P$js6ZH4X&I({R}rq|Q+S7B)=5_seBWgYQlEGdLiqQC1dcTRn$a<vKP#aPjL#ht2XuE+)t^93`{SN4fzxinv|El;OK2Nhh~pjqo<c5qAU@Z!MM&q^QBe{p3g!OZ-QYI%qjD%h0)U^<1t3%yy4JMQB}&=ZH=<ga2*OWdK%mr+Ct&oS7!WZ7QN^-vQK!Er6mnVb~x_0%x^mU^A$vDdLk$SuwUDfRZNnCPA9a#W*}J?NuC_{=85{TExButZ}FyO!*VqHEIJ=7D;A_6wng*=?c-o=6{;*qC(4DDpX=KN`Xgpw3<`pT1$m@U|JONP0PKBSHXGc>*Ufb_*yTp6u`^O)~>`k%AuN*ou6hzo<i)EGrZ>e*5x0BB$h~C0&o=P4<Uf$w*=NLJ`UBa74#ubu2;$1!V<uhAws2Cu%)?E5Ev3n8ZUl1QBowuMVz`xO7zbgA$PfuHfqlOHQF}XpojV~`k^n0K#n<1*zh@XC)w1YbTA8U7gG9BRg@h`mpr0dfm47(N1M(isv^j(Gy-5OhMqWlGeFnU^=8f(a3ok^OIt3F-q*CS4G41()S@v=QT!Ks*x`G`mTEz_iyU_8!~uC5&!X`i5Bfo?;WEKxpZT1XjHPPpjC_tN#d|0b>tG`acaQc_%AjbOaqFxPcX~R-0nrS>1}p3VujxCyIxh$eIcj`KQ?e1Vio&aI{{*-RcKSl=fb3>7F1mrx>+dqq<FSCEsRPSERrwFy%~VFso`TGqmjcV;KH*fO77nulICg`<G4m~XwCB~ZG3h#!xQnd%wm^0*X@Ag>v$mnj>E2GWB*vqy=?*o6eIuV&m}9TC_i|E^@a;IH<W%5MDirOY`ZVHu^Y-$|D*`T}x_p!mR;q$xN&e`wr181%_lbtk8XK~*)w0;d?K~u`rf2IFOo)Y(ENH8=-rd|(vQN2mS%4LjV<?Arv=(W!X<Px3L#~tsQ#wzLgJe@iojbz|!4*oE<52C~`p%U~0+H!NDd*M%6tUbHkIU%>aXX?F`)*~5K>JFAG+KPlWD)$Dv+nVv%u$ttks9<CYiPCNs)*(~;{m5EFCSxQ%!11<VL*s7N?M&f{A$?p$Hn5>v@{pS@rT0w2INP?1bllnO*z}NtKpY)2B3<|=S3065*l<jbIV!XWQ+@%8(LCjmBg%{3>OuZ9t*IQACw6%vuA4h_d;X%|4Suxya>mvp=)C{PZ#}t9QpMsyrs#hcw2G6N9&GIE|184%8PXb(QLbp+LTor=hg&nl){r)<~)ApebrT>fmx{x;#5bH78VeQNKN!0=ALc}QR)EW=CM+OQ)n>cqcBuKO2?~h7sBlnN>QS&S`Nz#3*KFpn6(Xfu@s!JWvO)RY4{?mkwd3txl66rD@3L(ffoD3fLh=>#nkm=b3D7Bw~rn3CJX{U>Z*vyS9r1>q|)Lu`o278G@2+}Aw;H?O=52zotEZ~%v`Bm8Q&VB&L>6fcxhtrbUg7bTA@NozATzG*s=vS#c~uyU?YX{dlieZ0=g9h2Z8OJgK^{&$i$P$3^ZThrVJ_?nWAjy{P3YwXt@Yi$vNU3?UXp4K!o50+Sji1X_o9N^i4-M^Kj&{QDcS~Ag?bA2tVGGh%j8DjZsmng=sO;u{4~99||1a5({cg63_%hxLyxXdhYMLX^NS%#tdG5V(NY#K>G*^812`gJTW!7SojC!+^e5A9oT)L@szb1!mWxChbxoow8)al`%)z!)5+GClLr%q%#V=t@MD7Y>K1T|dtOB42J$@7k>`wFA_%i3QGLbh^QwYqzno24sm~zwD$zmZRm-u)Caqf1klGSEqkz$Lw+2(-MjY}^Yd5Za2CT3rwXHaPCmH)vNS)P!y`-47DLBkHS%%Ko5(HmVLC3o`2};E2Z}SF>;(G?a4x3ZMYdj`_IW&(4^z>J^McmVf`5yL%&4Z8pI4v(r90qSjVV3dmj0f5RQs_DcM}<SrD$`M!i&IrK`MSaw6H}%)0`&tcedBUdR_KO0{?*^T1Vz(`@s|TH9<Bt1nF?NtZ^tLj6``tUL{gAtVxQyc>mqw!Ik6&tSVoGM>R|hV*c^7ro?N2`2Ovw?|NV<g5oKaQu#+Uk3oI4uZOZa69wy<L4Umo8UL$%EoFGB_v1+5n8FDm-q*R>=50U@Yxlbv>Kna^>vNyDZ!_c)S>2rDiGd)#LUB*H_F4i$@P;dQ(LP<$om8;ZvvXHVq3NdT928?ZTYouZjpRg{=iwn{K+v#<Yqq3%kwh1($0vG^a3Pgs0Ktoo**bax1h45ITwka|pks38m*Zdr`Nda;Um!who#c8k6d+kVDIVgEjk<>rzhiW*@IdoW5-|(S2`GM4OD9=<Ms&Iqc6q}9vx(>0{OQvfx#Tso)NS(WXiizrR7eC>dfL3E2Bog6~5Q^tf7oY{2)^>=+<a8K-)6=I{j&ZNX-Y=_Tr>$8caQ;ojZYca9DJ1jUp2w6-uoH3ANP8KqJk*%+9m;`3r`8?o$mFRc=>NE_))=EGL#@I&zc*-K5|Jp#&v`ikTWeqzFyF`Xe*aj|$O0(L$?FK~t6FHbK2zgifRQD;!z3&VL9YZiB1UvK`}LRa|L`y*ofiW{(QrpQ8=*8tZ?FU!Qpa%VWpXfQTdF%@a<zoTQX=JOg2E;Npla{JO0Q(QZo+&iG~u99ZT@u+@E)7=o)?*AspfFJZ#}UX7tUznKU9;?;kf5kCHn!>L=3%5b!T_a)Lh!vwsKR&pf5)Ao~&mj4M)3+h<Go0>P+)X65L4IKkS0do#A2<I{4(K>h#lzHS09*PWJ-vaW;4EsY@4->s1w+_rQ6}VEN@l6Apm1`vCfh3!wbxyTtkaXm$M)AR*o#`vt-{Vv~SU0<NqU7m?;J4O;KX1Trbb4cb;uV~q9Qp{lddE20p24WZ#@`=IC=0{m9hLXWsOkL<28d%k@vpCLT7oftPJ$Oz%KV{Sf1!=Nh(ZwlBmP6=?p-5&J_=lAN^^AbK1Q{5)7c?b#f`$wZ`*KN&z0lkt76??}rS*o^0soEq`yW{v>3bi`7NX^?QiQM5W2X|*>%DpRQ+v->6D|X@6pzLT*K(5c&t@l2&D!N{(kSl2*a-SehH!E|Kh|8g3co%f)p)uDWDR9-*!!7_-q;{A|CDK~>xWjT4rtK=t>WeH!)+YvxxzW>$Ub01Oh5_7ZD>4UhYKbn%%H@(2^sp-QSO<ah)@BrSWS9`jMq_TFjVChul@{&1_k>%j!RRCP4N2_3*3eFF0jV|ZhV#z;FjVTPR2p>$sQ2OE9>y}oU31&t9ZchiB{=C66?X<pd5WGFT${{6JnH+Rr#!Wsxu$AG(c09Bsu8PI@9XBvsnL1AVzFvecz}_4B}8KU>T>@?UN9%mULMUeTC-9Y^ormLf+(drLYs2tiGjD!R$qsi3e=q3GFPkVfF|xt(hlcfqL7tGTT}Y8NUdsIEn$QXt0-by;)Ha$Sh49cMId!)`Lg5HvOOCb@+bOKb;9sq@vYb;8f}0Z^wdf`kG8X^KtSw(s?g3GURw^dxhh93t6!`1E7M@o{PJk?kyclY_FG}ip@^NL<jnuWp;S@BRnlgrm(eITH(j7d_dMIk23i;LXy_K0zNXhvW}l@4hK3rvqF6SW5keg>u4KiovC&6X%|XPABJCiiFrd*zmI7&C;hg%LM*;F~t8K(o3?frAzTgexib3BVEZfGAa&m<XP%3LD!6asaz5dk*q_w-eMX;127F;mh*MPxW+LvY4mF1^WO6e|5UEi%F4-*f8(l*I>{3APj@^JQCylVWuJxw-n7$HjuRDZi$ODcH3AWWc%3|g3j%UH%y&PH{N?rjm;p;tu?>1M{6S$G9vwDh{)$&PmZrrpOGlBMYiPQ?LF4`5%TBDa#4GFS7%qM=@pEDN!3!V7C=i7A^m_MdjyN-CdWwq3}q*wIx5p0OYXsF0R}<#MjUPNV1AO3i0$of!S&Ks1J*pTAZg&aVE;$?du1bB;0>#h|;GCof<*7;W8X-intRN;hij@Eayk@3Wc^aMiaNWWR$_E!qqzh~{?np#Qa5k*IaDc-|RgwXi%@RlE5h>&u2tu`dnnu>NU<re23a!*^R9I7&P3>M}uv_dRdvd~2Jv!xlSZLc7T1jCLMh-6($>FsIANiIOej!xSn^M0h?N`rmzi_x|lKZyx5b7`UWzF4Vz-Y5;a|zjTs|;)S)$L{%)PmU;DPXHm-HWa-brabC!YRoW(Zrho&_M3CvCanF1N3)~fYd?Fzizrs4_=9M%DsB<H>s~Z&4q8Qtr&l4<PK;P~us*dTICX1y2>2PzP(Z)E={APGla&L&BYkSU<w9jVPZ|=5449zU~W%M#^7Cb#lF%*V2%>43w&4NKN3rrM;#8fPHIgL`82Cr*p4d<d)u!gIDqWlShiw-GUFI2Y~UVP<I)x&upv?Ul*^B{);Dms6T8=c%e0}qE0DJAan=Tb1XOZ3HdFmxb7`AjyLHsvzfs_5<tmVD&%h9Q!Zt3}a@nk<|U$5xt+*1Wi$ckHdG1uwi#THO0|LX5}^(OQ7q%=G_lk_pg`nlW-m{<tEi%-Jdnxy4kn@%qJa4W?b|bS-c8q#9YzT#ax2QlpjM$W=4ra?7-IlLDe#GZ&qPl~%wkHAN9j7CR_6$W|x2FX|GAdyd`?!r7ElDOBrJU8~S0AWR&Qlsv~che{PIr;_9ADh`p|Z(Zpnwb+cj#0F+dDjgPRWnd$4hd;@?PPuXmu@1L-g$7}@*=;$}+~-pHP#D)X2BwmBjA~`{%FT3QzO6Xj;@gx~<RqYFzg~Rw9Ic8hmdC6&L~J9`T#{atc#st+wr`|ql3}os4@>eF<UlA4htmisf4<n_S|@)tygrvsd6d|hFJqQHVPPiCX%XuX{R&VzdQwb4Uo{3q^aagV9iGvV{Hv*H#1~MBBk+R5%VZk@>V%b(NaK|{pSnB!LJAO$qbFf0y;Af79E{-#)(IJ0JpiYcW(r<|qMT>MuD^?VF9}{dK}n`3^yB{m*aO<A')).decode('utf-8'))
__version__ = 'BL-V17-R1-RC2'

_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25
_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}
_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_SELLABLE = tuple(_MARKET_PARAMS)
_LIQUIDATION_ORDER = (
    "CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
    "STRAWBERRY", "TOMATO", "WHEAT", "WOOL",
)
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 0
_SHIFT_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
}
_PREEMPT_ENABLED = False
_PREEMPT_FRACTION = 2.0
_PREEMPT_MAX_BATCH = 30
_PREEMPT_MAX_CLONE_DISTANCE = 6
_PREEMPT_MIN_PRICE_RATIO = 0.0
_PREEMPT_MIN_FUTURE_QUANTITY = 4
_PREEMPT_START = 120
_PREEMPT_STOP = 680
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _shed_access(size):
    half = size // 2
    return {
        (half - 1, half - 1), (half, half - 1),
        (half - 1, half), (half, half),
    }


def _projected_shed(obs, action):
    farm = _farm(obs, _seat(obs))
    private = _get(obs, "private", {}) or {}
    projected = {
        key: max(0, int(value or 0))
        for key, value in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = list(_get(private, "inventories", []) or [])
    positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles = list(_get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(unit_actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        inventory = {key: max(0, int(value or 0)) for key, value in dict(inventories[index] or {}).items()}
        if unit_action and unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action and unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if structure and isinstance(tile, dict) and tile.get("kind") == structure and not tile.get("animal"):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


def _public_signature(farm):
    keys = (
        "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
        "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED",
    )
    counts = {key: 0 for key in keys}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "")).upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (
        len(_get(farm, "hands", []) or []),
        len(_get(farm, "unlocked_quadrants", []) or []),
        tuple(counts[key] for key in sorted(counts)),
    )


def _clone_distance(obs):
    farms = list(_get(obs, "farms", []) or [])
    if len(farms) < 2:
        return 10**9
    left, right = _public_signature(farms[0]), _public_signature(farms[1])
    return (
        abs(left[0] - right[0])
        + 3 * abs(left[1] - right[1])
        + sum(abs(a - b) for a, b in zip(left[2], right[2]))
    )


def _shift_state(obs, step):
    seat = _seat(obs)
    state = _SHIFT_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due_step": -1, "due": {}}
        _SHIFT_STATE[seat] = state
    state["last_step"] = step
    return state


def _repay_shift(obs, action, step):
    if not _PREEMPT_ENABLED:
        return action
    state = _shift_state(obs, step)
    if int(state.get("due_step", -1)) != step:
        if int(state.get("due_step", -1)) < step:
            state["due_step"], state["due"] = -1, {}
        return action
    due = {item: max(0, int(quantity)) for item, quantity in dict(state.get("due") or {}).items()}
    market = []
    for raw in action.get("market", []) or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and due.get(order[1], 0) > 0:
            item = order[1]
            requested = max(0, int(order[2]))
            reduction = min(requested, due[item])
            requested -= reduction
            due[item] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action["market"] = market
    state["due_step"], state["due"] = -1, {}
    return action


def _future_sells(step):
    if step + 1 >= len(_ACTIONS):
        return {}
    result = {}
    for raw in (_ACTIONS[step + 1].get("market") or []):
        if len(raw) >= 3 and raw[0] == "SELL" and raw[1] in _PREMIUM:
            result[raw[1]] = result.get(raw[1], 0) + max(0, int(raw[2]))
    return result


def _preempt_shift(obs, action, step):
    if not _PREEMPT_ENABLED or not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    state = _shift_state(obs, step)
    if state.get("due") or _clone_distance(obs) > _PREEMPT_MAX_CLONE_DISTANCE:
        return action
    future = _future_sells(step)
    if not future:
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            item = raw[1]
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    shifted = {}
    for item in _PREMIUM:
        future_quantity = max(0, int(future.get(item, 0) or 0))
        if future_quantity < _PREEMPT_MIN_FUTURE_QUANTITY:
            continue
        base_price = float(_MARKET_PARAMS[item][0])
        if float(_get(prices, item, 0) or 0) < base_price * _PREEMPT_MIN_PRICE_RATIO:
            continue
        target = min(
            max(0, int(remaining.get(item, 0) or 0)),
            future_quantity,
            _PREEMPT_MAX_BATCH,
            max(1, int(round(future_quantity * _PREEMPT_FRACTION))),
        )
        if target <= 0 or len(market) >= 10:
            continue
        market.append(["SELL", item, target])
        remaining[item] = max(0, int(remaining.get(item, 0) or 0) - target)
        shifted[item] = target
    if shifted:
        action["market"] = market[:10]
        state["due_step"] = step + 1
        state["due"] = shifted
    return action


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE[seat]
    if step == 0 or step < game.get("last_step", -1):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game["active"]

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - transaction["start"]
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
        else:
            active.pop(actor, None)

    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "PLANT"):
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)



_V17_R5_MARKETS = json.loads(zlib.decompress(base64.b85decode(
    "c-p;M+is&U5d9aPc>von<S}hoHCozKq*c_7M*IJNu~cDG40E%AN|hRs_<}v>%$Z|fuh;D1<MZ!ZcY6AGe9!Xi^4uKy|D}Wcnmr%8CKEn<H9x!_Uk+{G`tfw>+s+=JpPS|_%iaGk&Q0^wKYnT2(`%ORCXa_H?7oNTKV7qP)3)E=?(x1X-k166V)@@_J}dP%ywtCzdq1|vKTQ|B_jH|S+f>1*FMK1(wk5C)J+KpJyHx#R$wGv?TTULI-@C)*q3OEMuYj0sUBuM5pQ^e^Tl*5$h?vO>bLbk+X1ca1(@YPY#7G!#xnpQ4A_!J^>EuBSth-X^Mss0J04yE}Q{FBs5@rl~CvSW?o!TJ<AZu{X0qx=SX|&m4I2dGIn8EsaD-&W=t~BJzav|WD=-=ZUY59SYsmdzy3%W;fI7<X0I(8+b6Pvb+6z|e08QDEET{PV$?SP|i4M|P213nE8;_6zUzA1~P5aLi83L<U1D1&bp<mK4@9!m=C7$K9?AwMl&lhHG5*?kgEg}S;D*^(eCd>wC{-U5O^Ld_5hQATi?WCpCEm8XZ<F|+eTcV&><r$Y%-z@fW1>(Bv1px-5-goHiCX{F5GYrn9hifb{O>C;Rf-4ug(U?`sCw$h-23djb=Z4oPofDqyrCnZ7srio*dq*M(=D)=zTjnYE0N<!nrK`IK^cA8gHDEje!?qLHZms~zs5_zQsAzQ6UI&}I96hR%d$AW6Y9=X8Uq)NmUf`fFCt%{Uk?F~?xsMgk|oX{~VLL^=&>5zV(c&JTsQiN-Zt5BLMc8E?lp$ZcU3l;N^d%QWzVWQe0(PG>NvWRF$<1{2pw3sB*uT8aH4J`9>!*WBHO|cy9n26;H9GZSHI;-eW>J=5=0$<F)GN*3+o*gXqmSapihqFzc7^gX7G*ht~47}e)7e(cDu4IaL28JK(lf;)L6Jnf7H6#+l)UC)TcrTuYdNGqe@wNp*zdw@mohJ#ef><v=t*HjXfi4P(zGof`I}>W!lGQjvY(5)#2b38yRR{E$E*@t!GMf9DTq4Q}1A=p^VC|{ol*~%G75Sq)f<JiOSIl>|QkF?W{ou5@78f%)Ixkw}*kTLkNufIzot4(w(lbh<$i5VBjD^)VmH^z=iye_cM)HObAM6n<cZwPZChjhaz`?4*Y*c;6TX=kZ#!-P?Nrx>uFdDx)b3!Sno*}jiU?W22@0t0>xHXiBB8=byze2@Z*QkAy2B<J@wozf2&B&mGx;#PD@M`T*A)Uxj5w70E_$!tJt=E%N&Glo1n^=PE3G8huMlegI_~GOr_}w%-qt75L@Q2!X7-|Z?8`F7CC5C5J@(sHPuJ`;(VI@-@f3+!o>&1&9#GwiHj_PYDgRMcQ3c8XkF$C?o0KlYLp)wKfSDu*5C^L`9ud{Ed-W|<Uk^;zC3Q~wY)ceKkvYb=w8iXKu6u+P|tD)`6s8S!Z^Yma0IWGhPHTh5lz5xRsba$8T{m&A*!4L2aQC`i0!$X7wxuFpL0hMf{p8"
)).decode("utf-8"))
_V17_R5_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL')
_V17_R5_FRACTION = 1.0
_V17_R5_STATE = {
    0: {"last_step": -1, "target": False},
    1: {"last_step": -1, "target": False},
}


def _v17_r5_signature(obs):
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    cows = sheep = 0
    for row in list(_get(opponent, "tiles", []) or []):
        for tile in list(row or []):
            if not isinstance(tile, dict):
                continue
            cows += int(tile.get("animal") == "COW")
            sheep += int(tile.get("animal") == "SHEEP")
    return cows, sheep


def _v17_is_r5_family(obs, step):
    seat = _seat(obs)
    state = _V17_R5_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "target": False}
        _V17_R5_STATE[seat] = state
    state["last_step"] = step
    if not state.get("target") and step >= 24:
        cows, sheep = _v17_r5_signature(obs)
        if sheep >= 4 and cows <= 3:
            state["target"] = True
    return bool(state.get("target"))


def _v17_town_demand_at(obs, item, step):
    demand = 1 if item != "FERTILIZER" and step % 24 == 0 else 0
    if step % 4 != 0:
        return demand
    town = _get(obs, "town", {}) or {}
    for shop in list(_get(town, "unlocked_shops", []) or []):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand


def _v17_pickup_reserve(action, item):
    reserve = 0
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    for order in orders:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == "PICKUP" and order[1] == item:
            reserve += max(0, int(order[2])) if len(order) >= 3 else 1
    return reserve


def _v17_r5_counter(obs, action, step):
    if not _v17_is_r5_family(obs, step):
        return action
    future = step + 2
    if future >= len(_V17_R5_MARKETS):
        return action
    targets = {}
    for order in _V17_R5_MARKETS[future]:
        if len(order) >= 3 and order[0] == "SELL" and order[1] in _V17_R5_ITEMS:
            targets[order[1]] = targets.get(order[1], 0) + max(0, int(order[2] or 0))
    if not targets:
        return action
    action = _copy_action(action)
    market = [list(order) for order in action.get("market", []) or []]
    shed = dict(_get(_get(obs, "private", {}) or {}, "shed", {}) or {})
    for item in _V17_R5_ITEMS:
        planned = targets.get(item, 0)
        if planned <= 0:
            continue
        # R5A moves this base sale to step+1 only when town demand does not
        # refill the product before it acts.  Counter only that clean case.
        if _v17_town_demand_at(obs, item, step) > 0 or _v17_town_demand_at(obs, item, step + 1) > 0:
            continue
        existing = sum(
            max(0, int(order[2] or 0))
            for order in market
            if len(order) >= 3 and order[0] == "SELL" and order[1] == item
        )
        available = max(
            0,
            int(shed.get(item, 0) or 0)
            - existing
            - _v17_pickup_reserve(action, item),
        )
        quantity = min(
            available,
            max(1, int(round(planned * _V17_R5_FRACTION))),
        )
        if quantity <= 0:
            continue
        current = next(
            (order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item),
            None,
        )
        if current is not None:
            current[2] = max(0, int(current[2] or 0)) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
    action["market"] = market[:10]
    return action


def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )


def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    current_quote = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)


def _demand_per_day(obs, configuration, item):
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    turns_per_day = int(_get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = max(1, int(_get(configuration, "townShopSellInterval", 4) or 4))
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
    if item != "FERTILIZER":
        center_interval = max(1, int(_get(configuration, "townCenterSellInterval", 24) or 24))
        demand += turns_per_day / center_interval
    return demand


def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item = str(order[1])
    quantity = max(0, int(order[2]))
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)


def _rank_sell_slots(obs, action, configuration):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows = [
        (_order_score(obs, configuration, order), -index, list(order))
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
    return action


def _terminal_liquidation(obs, action, step):
    if step < 716:
        return action
    action = _copy_action(action)
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    planned = {item: 0 for item in _SELLABLE}
    for order in action.get("market", []):
        if _is_sell(order):
            planned[str(order[1])] += max(0, int(order[2]))
    for item in _LIQUIDATION_ORDER:
        available = max(0, int(_get(shed, item, 0) or 0))
        extra = available if step >= 718 else max(0, available - planned[item])
        if extra and len(action["market"]) < 10:
            action["market"].append(["SELL", item, extra])
    return action



_V17_MD_MARKETS = json.loads(zlib.decompress(base64.b85decode(
    "c-q}u&2HN;41O1%eF$a8KgYE7&|qm(xE+eF5cd9Wv35zD*d`^CqMcws4}~q$6h(ggNK1Ktf6wl>eV6&1_s`9*w?CW5?Zal5<=O52HOt-P^7DPyJ)PZn?z+2=%dhv{<|WJP(dCD3w|~rX_#Xb$@9%!yzMP(@{Ku{L?77?RP8W;Mi|2pD!)`o|9ty}%tG{pce{}uJcDMcA^`CQ~ro2YAjxLauC7d^zU&-~VZ|yM$gOS7BZu)+2w_FyQ)1Hfl!1^@R;SD$Al-8fR3}dLlBN`-gK2G5IrQf{XbbbGJoCWzV^Z^_aFgc;IJln`Up0;O#m5Sh`gEKtYWWV2?dD(9Bc$eW~osZ9*5=%-N1!V0Lt;~1^U5ZMWnLriY!%!`K5R&Z?mS=@@%z_m@;bBxiY<E8~!&_MRJW5Jj892ATz_Y*9PFk3NLc|UB@(r=B4EVJ$ty1hmD2B?|6EhYhT9ux-Mhh#W;grG#dDJRs2i|a6t=jX${3AZ;l%#kF8qDz|qpJ{>$ON%Q4=M(02|!O~XkJW4Y=TZCp^9M&E{TNh>5U?)4~6r?1p7@qEFj+%-XJ7p!4|f15boIt6nt_9VI>%B?b7Ljd`V~vH9i7yK6r<pju8npJE+c|Y69|dl>&6U&vNIGXB#}S@q~ewiwh-6c6reH*~r?+RIOnkA!1xSoT3e^mBLS0gcqfcnmf5_JpxX<v~OY+9%a>$+GL_{)p$soy7h7_YZTJJ(YGooHbN!hiy)S7F65lJQ~_!%6Rw}rKbWU@Aoyqpg<11sdK83N+(OYRZ!NXVO6o|A$(j399*GLgXMUhGdcfJeVU)lSyN7+Sow{0mxx_%jY#t)URFq3Vt&qUQ8nc?@ZS_PX{bdUvQ8dV^@D<b8kr=NPeBPGnLurzcoRy2Mg`*iz5W`s)Sj$k8KHA@aiZEcK=k^E5jY*T0k;@tdM=ZUZaXQ6&#B{`YO>02-5>tK6Cb*W0QalhQbrb*ReN2WctH4?n(3M0AlBeq&`<xoevPi~5{aZj|TTx~&MWaD9dX>&G$kDYue@P}O=`6>fw5_FtT|y*k3su0%2ehv|z@KXw`1fT!cL|^icKrDJUgF=T(S}>iH&1gN^;YzIpp&?ls6uLtQV3;q5lpv6%2czxv^8jWsZA2aIL(*s(gOb6HDjn%2B9`~N?*FRFjlp!kl}PjAHW$c)=T!cctH``zFlG$1A8xu@CVogUhNhdJZX$_<Fa0!d)4XuI|Zr^q@z^NdrDe_b~{n<Sr8b9JvSrex6u%ivca*{wvf(olm!Z95yxw<k@NG}r>uyV_Zg6N7V&G4aW4^!w3k=pfG09VoJf%(85qafx`bMQ;(dD8gYwdif&|@Z41z|md6Z@~!eXw~u3wbznALcE8eP!FEr|UX>1QMwY<G{IiN|-hvFNk&+^r7LR<mZ$M8R}fr*K)vlnt7Ko!gl&xWcC}OWG;Yz7UjI=xMn%c~}d`xM>3WRU8W^28{NyCo38+I}$1E0V=3c#os0+tO-qcTZJ$IE8fD+uSH_%=Ip-+IrZ~{oP?`7*Y?9}{pw=<N*c=Yxr$z^ih8+~h)jq{q@qWh!lmHptnkHC!?cc`Ce0ZrO6c$@fS#mis90_Dy2{|gfdzU+l|C}{l~vwn_rX9}&&2mo$amNpOlM&sG*@jo$CnPPj>H5s*N;Nv`K?e~m)uSfaxg_#y0wVdLWYQ@AB_2^$Lg+dt01*gtNSo9?NmxIkV#=S%=HFc_<<!`R^xCI7K7Ro*@JwMAXof=0lB3G{C{)tY>PDWI2CXXeoT5QUp`SSbJ~b`hBWq*6f~AjCK%}>pzSFj2Kv8<5=ij"
)).decode("utf-8"))
_V17_MD_FRACTION = 2.0
_V17_ROOM_GUARD = True
_V17_FEED_GUARD = False
_V17_MD_ITEMS = ("MELON", "MILK", "STRAWBERRY", "WOOL")
_V17_MD_STATE = {
    0: {"last_step": -1, "target": False},
    1: {"last_step": -1, "target": False},
}
_V17_FEED_RESCUE_STATE = {
    0: {"last_step": -1, "day": -1, "active": {}},
    1: {"last_step": -1, "day": -1, "active": {}},
}
_V17_ROOM_EVAC_STATE = {
    0: {"last_step": -1, "day": -1, "active": None},
    1: {"last_step": -1, "day": -1, "active": None},
}


def _v17_md_signature(obs):
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    cows = sheep = 0
    for row in list(_get(opponent, "tiles", []) or []):
        for tile in list(row or []):
            if not isinstance(tile, dict):
                continue
            cows += int(tile.get("animal") == "COW")
            sheep += int(tile.get("animal") == "SHEEP")
    quadrants = len(_get(opponent, "unlocked_quadrants", []) or [])
    return cows, sheep, quadrants


def _v17_is_md_family(obs, step):
    seat = _seat(obs)
    state = _V17_MD_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "target": False}
        _V17_MD_STATE[seat] = state
    state["last_step"] = step
    if not state.get("target") and step >= 160:
        cows, sheep, quadrants = _v17_md_signature(obs)
        if (quadrants >= 2 and cows >= 4 and sheep <= 2) or cows >= 9:
            state["target"] = True
    return bool(state.get("target"))


def _v17_md_pickup_reserve(action, item):
    reserve = 0
    for order in [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == "PICKUP" and order[1] == item:
            reserve += max(0, int(order[2])) if len(order) >= 3 else 1
    return reserve


def _v17_md_counter(obs, action, step):
    if _V17_MD_FRACTION <= 0 or not _v17_is_md_family(obs, step) or step + 1 >= len(_V17_MD_MARKETS):
        return action
    targets = {}
    for order in _V17_MD_MARKETS[step + 1]:
        if len(order) >= 3 and order[0] == "SELL" and order[1] in _V17_MD_ITEMS:
            targets[order[1]] = targets.get(order[1], 0) + max(0, int(order[2] or 0))
    if not targets:
        return action
    action = _copy_action(action)
    market = [list(order) for order in (action.get("market") or [])]
    shed = dict(_get(_get(obs, "private", {}) or {}, "shed", {}) or {})
    for item in _V17_MD_ITEMS:
        target = targets.get(item, 0)
        if target <= 0:
            continue
        existing_quantity = sum(
            max(0, int(order[2] or 0))
            for order in market
            if len(order) >= 3 and order[0] == "SELL" and order[1] == item
        )
        available = max(
            0,
            int(shed.get(item, 0) or 0)
            - existing_quantity
            - _v17_md_pickup_reserve(action, item),
        )
        quantity = min(available, max(1, int(round(target * _V17_MD_FRACTION))))
        if quantity <= 0:
            continue
        existing = next(
            (order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item),
            None,
        )
        if existing is not None:
            existing[2] = max(0, int(existing[2] or 0)) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
    action["market"] = market[:10]
    return action


def _v17_move_toward(position, target):
    x, y = int(position[0]), int(position[1])
    tx, ty = int(target[0]), int(target[1])
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _v17_feed_guard(obs, action, step):
    hour = int(_get(obs, "hour", 0) or 0)
    day = int(_get(obs, "day", step // 24) or 0)
    if not _V17_FEED_GUARD or hour < 18:
        return action
    action = _align_hands(action, obs)
    seat = _seat(obs)
    state = _V17_FEED_RESCUE_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)) or day != int(state.get("day", -1)):
        state = {"last_step": step, "day": day, "active": {}}
        _V17_FEED_RESCUE_STATE[seat] = state
    state["last_step"] = step
    farm = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    positions = [_get(farm, "farmer", [4, 4]), *list(_get(farm, "hands", []) or [])]
    inventories = list(_get(private, "inventories", []) or [])
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]

    threats = []
    for y, row in enumerate(list(_get(farm, "tiles", []) or [])):
        for x, tile in enumerate(list(row or [])):
            if (
                isinstance(tile, dict)
                and tile.get("animal")
                and int(tile.get("consecutive_unfed", 0) or 0) >= 1
                and not tile.get("fed_today", False)
            ):
                threats.append((x, y))
    threat_set = set(threats)
    active = state.setdefault("active", {})
    for actor, target in list(active.items()):
        actor = int(actor)
        if actor >= len(positions) or actor >= len(inventories) or tuple(target) not in threat_set:
            active.pop(actor, None)
            continue
        inventory = dict(inventories[actor] or {})
        if int(inventory.get("WHEAT", 0) or 0) <= 0:
            active.pop(actor, None)
            continue
        if tuple(positions[actor]) == tuple(target):
            orders[actor] = ["FEED"]
        else:
            orders[actor] = _v17_move_toward(positions[actor], target)

    claimed = {tuple(target) for target in active.values()}
    remaining_actions = max(1, 24 - hour)
    for target in threats:
        if target in claimed:
            continue
        if any(
            tuple(position) == target
            and actor < len(orders)
            and orders[actor]
            and orders[actor][0] == "FEED"
            for actor, position in enumerate(positions)
        ):
            continue
        candidates = []
        for actor, position in enumerate(positions):
            if actor in active or actor >= len(inventories):
                continue
            if int(dict(inventories[actor] or {}).get("WHEAT", 0) or 0) <= 0:
                continue
            distance = abs(int(position[0]) - target[0]) + abs(int(position[1]) - target[1])
            if distance + 1 <= remaining_actions:
                candidates.append((distance, actor))
        if not candidates:
            continue
        distance, actor = min(candidates)
        # Do not seize a worker early; start only at the last safe moment.
        if distance + 1 < remaining_actions:
            continue
        active[actor] = list(target)
        claimed.add(target)
        orders[actor] = ["FEED"] if distance == 0 else _v17_move_toward(positions[actor], target)
    action["farmer"] = orders[0] if orders else ["PASS"]
    action["hands"] = orders[1:]
    return action


def _v17_room_evac(obs, action, step):
    if not _V17_ROOM_GUARD or step < 648:
        return action
    hour = int(_get(obs, "hour", 0) or 0)
    day = int(_get(obs, "day", step // 24) or 0)
    seat = _seat(obs)
    state = _V17_ROOM_EVAC_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)) or day != int(state.get("day", -1)):
        state = {"last_step": step, "day": day, "active": None}
        _V17_ROOM_EVAC_STATE[seat] = state
    state["last_step"] = step
    if hour < 21:
        return action
    action = _align_hands(action, obs)
    farm = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    positions = [_get(farm, "farmer", [4, 4]), *list(_get(farm, "hands", []) or [])]
    inventories = [dict(value or {}) for value in list(_get(private, "inventories", []) or [])]
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    shed = dict(_get(private, "shed", {}) or {})
    total = sum(max(0, int(value or 0)) for value in shed.values()) + sum(
        max(0, int(value or 0)) for inventory in inventories for value in inventory.values()
    )
    access = _shed_access(len(_get(farm, "tiles", []) or []) or 10)
    if hour == 21 and state.get("active") is None and total > 100:
        candidates = []
        for actor, (position, inventory) in enumerate(zip(positions, inventories)):
            saleable = sum(max(0, int(inventory.get(item, 0) or 0)) for item in _SELLABLE)
            if saleable <= 0 or actor >= len(orders) or (orders[actor] and orders[actor][0] != "PASS"):
                continue
            target = min(access, key=lambda point: abs(int(position[0]) - point[0]) + abs(int(position[1]) - point[1]))
            distance = abs(int(position[0]) - target[0]) + abs(int(position[1]) - target[1])
            if distance <= 2:
                candidates.append((distance, -saleable, actor, target))
        if candidates:
            _, _, actor, target = min(candidates)
            state["active"] = {"actor": actor, "target": list(target)}
    active = state.get("active")
    if active is None:
        return action
    actor = int(active["actor"])
    target = tuple(active["target"])
    if actor >= len(positions) or actor >= len(inventories):
        state["active"] = None
        return action
    if tuple(positions[actor]) != target:
        orders[actor] = _v17_move_toward(positions[actor], target)
    elif hour == 23:
        orders[actor] = ["DROP"]
        market = [list(order) for order in (action.get("market") or [])]
        existing_sales = {}
        for order in market:
            if len(order) >= 3 and order[0] == "SELL":
                existing_sales[order[1]] = existing_sales.get(order[1], 0) + max(0, int(order[2] or 0))
        needed = max(0, total - 100)
        priority = ("WOOL", "MILK", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "FERTILIZER", "WHEAT")
        inventory = inventories[actor]
        for item in priority:
            available = max(0, int(inventory.get(item, 0) or 0) - existing_sales.get(item, 0))
            quantity = min(needed, available)
            if quantity <= 0:
                continue
            existing = next(
                (order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item),
                None,
            )
            if existing is not None:
                existing[2] = int(existing[2] or 0) + quantity
            elif len(market) < 10:
                market.append(["SELL", item, quantity])
            else:
                continue
            needed -= quantity
            if needed <= 0:
                break
        action["market"] = market[:10]
    action["farmer"] = orders[0] if orders else ["PASS"]
    action["hands"] = orders[1:]
    return action


def _v17_room_guard(obs, action, step):
    if not _V17_ROOM_GUARD or step % 24 != 23:
        return action
    action = _copy_action(action)
    private = _get(obs, "private", {}) or {}
    shed = {key: max(0, int(value or 0)) for key, value in dict(_get(private, "shed", {}) or {}).items()}
    inventories = [dict(value or {}) for value in list(_get(private, "inventories", []) or [])]
    carried = sum(max(0, int(value or 0)) for inventory in inventories for value in inventory.values())
    farm = _farm(obs, _seat(obs))
    positions = [_get(farm, "farmer", [4, 4]), *list(_get(farm, "hands", []) or [])]
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    produced = consumed = 0
    for actor, order in enumerate(orders):
        if actor >= len(positions) or not isinstance(order, list) or not order:
            continue
        tile = _tile_at(farm, positions[actor])
        if order[0] == "HARVEST" and isinstance(tile, dict):
            produced += max(0, int(tile.get("yield_units", 0) or 0))
        elif order[0] == "COLLECT_FERTILIZER" and isinstance(tile, dict) and tile.get("fertilizer_available", False):
            produced += 1
        elif order[0] in ("FEED", "FERTILIZE"):
            consumed += 1
        elif order[0] == "PLACE" and len(order) >= 2 and order[1] in ("GOOSE", "COW", "SHEEP"):
            consumed += 1
    market = [list(order) for order in (action.get("market") or [])]
    planned_sells = {}
    planned_buys = 0
    for order in market:
        if len(order) < 3:
            continue
        quantity = max(0, int(order[2] or 0))
        if order[0] == "SELL":
            planned_sells[order[1]] = planned_sells.get(order[1], 0) + quantity
        elif order[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
            planned_buys += quantity
    actual_existing_sells = sum(min(shed.get(item, 0), quantity) for item, quantity in planned_sells.items())
    needed = max(
        0,
        sum(shed.values()) + carried + produced - consumed + planned_buys - actual_existing_sells - 100,
    )
    if needed <= 0:
        return action
    # Finished animal products and sale-only crops are safest to liquidate.
    priority = ("WOOL", "MILK", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "FERTILIZER", "WHEAT")
    for item in priority:
        already = planned_sells.get(item, 0)
        available = max(0, shed.get(item, 0) - already)
        quantity = min(needed, available)
        if quantity <= 0:
            continue
        existing = next(
            (order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item),
            None,
        )
        if existing is not None:
            existing[2] = int(existing[2] or 0) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
        planned_sells[item] = already + quantity
        needed -= quantity
        if needed <= 0:
            break
    action["market"] = market[:10]
    return action

def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _v17_feed_guard(obs, action, step)
        action = _v17_room_evac(obs, action, step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        action = _v17_r5_counter(obs, action, step)
        action = _v17_md_counter(obs, action, step)
        action = _v17_room_guard(obs, action, step)
        action = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }

def _kaggle_submission_entrypoint(obs):
    return agent(obs)


# --- E279 demand-dominance selector (our bounded modification) ---
# LOW: Boatlee BL-V17-R1-RC2, preserved above byte-for-byte.
# HIGH: Kawashigi public episode 92521336, seat 0.
# Both route streams are identical through runtime step 167.
_E279_LOW_ACTIONS = _ACTIONS
_E279_HIGH_ACTIONS = json.loads(
    zlib.decompress(base64.b85decode('c-rk<U2j`ia{MoP*29pZC@F6mn;RRe85y#@#AYB22FL~hg3ZGuZ^8ceII=`u-cwy&)#uQXCwil4>fZBxx~r?JfBB!2fBWtCzyIy`lYjc<<j2qNZ{Gg;;ripJ&v%=X`_q$u|Ls5j^}oLS&zFyX|Lynx_}hPf`TWbtyY~<Ot9|(K^Iw0x{`vh+*Ec7pCvR@IC#TEi>yPg?n-7!!__*1;{qptp-RAn!$?3)H>z_6^w?ChpE_OfvaCiIm^P5lmzgXYj|KoJpu@CRx{Q2{T{hJn(zWs8t-F*D?(AJ-C?>@bI__X_K_Tg|KK5lMq_HR9#zxC;HlUIR;OkcbIG@lC8fZ6N9*@HdYwd7$=76*NO{1tiEhnwp+n`k^yf1dsTylvKQ^47;cnT}`Ej)(7l-Y<rOzCO-W@UwJ;H`nv`@0Z8*r_J4b5zW6lTs?5<F6WEr<L&49B5D`spZ;%W9DFnD9h=H_a1IA}HcI>cy}5o|nomFax-%zTx8`y`T<uGrMq&D^bh^O)Lz4q`LbHO&TOP+AjM-#3ni*?<qtDpmxYMCKc<y}X?T4_PreIwzgu@MNhVW?RXUjnsw2?)JPCj{0E!D?T{wAMCFocgM449*A-t<A-y<_*`%h~%8eeecuKkhvbe*7h!^s&#U6F#H^Pk%dk)6nOpAD-c{vs>jXuqKnk)VM&#JavAyI@|Y~w_t9Mke@bY#F!SmxxKmBy!rI&pEh@&-rv0cm%}q*(BPF{Vl0vJJB~C5Pq+4@J>eeOIU=(k2Uq#|y<q{q==E>R@4Szzx_6t}f1Nf7Fz*`kabkpng<J76fH4C11n$-2(zeWG-iK*#vp%K+2poIEAZ4x!{FFVAjRpFYK9G3?qW#$6kH$?dI#BVTO17`Efv9hu&p+{W`dnWHcuF4!y=B9B0LK0Pk*zV9Z~hiIA+}}SKI?I*sY-COZ){k<K5hKd<a;03P%9PWt{Voit<WCMhcNnL28(|=_3myFQX?IQ?5dRx$%_53d+X%D^6yTu?LD2dh7cj^U3UV#U%QMAdeK&fh1)S96zMokS^EvMiCP}SWGL8UbkXlozZ4rK=v6WpIb`S@ymKh)j{{u2KKAvo-{E6*0BeM)6Gz@*2tS3K&TRlC2+6naZai4#&T05c(Q7pDl)eCDW)W3D5D%4d+E1eDy^buq;DfPwcYXJlsAJ=9d;={Iqu6Muc6})h(R3_&C<g7|v@ysXnV<_u;e)>G*w?pugN}@<-JncIDu+V=zH+ea_G|QMQ1%f|dC>PyL|4u9eG>y+$6)3h4SJt}H&i0b?SosI)T`O>`q*BO=sdHW9)EZFu-#i@>Kqdv7mjK5XvBQ{ba%b|adUU~S76DM5T>+4;oBh%b2%JtVhs!$vA9118ubl9DC_Pt%*Z(uRlQ4NWT6T?9m~X;S|?Mi$wQbpsM57Qb{}?Edj2>KXM4JlCz}?NUk8RdyS$V62ozUA)NkwSug$Dlgy_@PhE_tX?JY+LZvt1_d0Yi1JQ^MEHL&$uVY0P@9i4aDHD~vQ<5P&2B{l*vRM7FNIMdWu&%l_<wZhPf$tAeGy}fxzi-D%q<9|L*(3kV^?Md0z+xzplx5n4f(W#k(j3P0Jvoas*=vI&o-osh3*Ya*6L{JXKk}m}I56Dy+Z77tci1{H}d`!KsB^auU9;W*)ee9?<`k5kS5_;QwD&w7-C_ln$B7jZj;aIPU2xXjbrVbMex_5!m`F6U|(KkOWD%*e!Gy0?t3OIFI0C}D|Q)7GqpJZm<9?Obao7u99Qp66JUke<wTjf?6%x1MsHIYuGIl*%1YsR_oz!H?%3o=oIHh`;{U3EH=q4?U_00m#Sw|wwJ4mYT037c$~&6}rgd)9+=r_*e`m<Fc64GcWnMV$;J5X}E|l5NdM<-5QX$#zb1PkSs2wu5N$sh(@j@>}f{2>+ndIGzn;N&o|6rr*HCzi0!)U@GD^7Qx6cT#S3l?3;?Q0jz^2MB8M;TO;0fKD2aB#s4djE!jKT52X=r7dIJ8@^Y3a3{c<he45+_ZU4_Y@7S=?uCYHUI!Y<XOCWdl|Ftv^mX5;Gt^0CI<n-_w2n!5sJ#)PFN<b3P9F=~m;Nl1DcQk15lM(UL`<p)>`c%;4LS_Q|8H<PS-gRW(>nz8TcK0hX>vU7lCFuoT7-SUzYcTRInrmC3cyd6hj!)>=e8tt&pPnAfYzu((5xg&3EUmeE;MbGX2xTh?42|msKn7w%$m5W`TSatA_E9P0T3tMvTUkQDHA+Y8+3ziSX7peNVIMTv`Vzq6CUGt<0~UKlW?tJh33LE=h<QPn_h}kR#8+qs61ATA&M;8c!wyy8=hGxu(+CfEa|)=XU}^$umJBW024FLFo53h(!3F3*6Q?V$<r!BDWzbbgYpT`jYrbj!ypmV27p#ll9a5FE^N_U+*}01f?ML#*SQqwBl9FeHM($?aYl!606!Ia#91n4##-~sY`S9A9@4hkJLBm6e^f{H+Evp$YG26Yi0#*SezteQA25K<0_L=TY6B4f%<IFkULp*8{{j*p>jW2X2!2;OUP*W?5x=@3&H~}KQTO}x>f;{I6Hk1C1{3Zcb_{ud~;T4E1><S3NKXC%e0Vi%{B=j~tOx&?V8iNMd3N5$t1RQ*frbM)CjZP<>JK}tFiGRtJG1Q}J8^e`g0mLb~K{!34%=K}pNJxwYBUuQR_N))KNw^u4V2v0!*E}wrm_>Y5zUmOKBewO>S}wE=Wc@z9fjC=IAdJbj)Nyp?@DYD(tQ}37RU5S-twLt=afXIBtA6kt+clEJO|ETazUN(W&)6zpvA%?6y)LW)yHm#sj_K!j2icF|&R3%2Vh~!7juS`z0B-kPdCh~Dt>nv64oeU`u!zJJU$;Ub)5GGrdmeR3P-^rt{8=Dea{h2wu`EJBMHsVpNqAK3i`Qly#67dgOQoS`R%qu;)8U%FL=3xkDoAq|kz{z_$Tk2aP`Vv}e-{hm4#2N$+YNt*<T!Z&FVNfz<3`Y^4HC%|Y{7hFFYa{$DjQAeH<KK|D5n~?_7X)p^bVl6<6X>1w*<B-^<W*dBNz7u4FD}A&{PfYlAzeUXF3E!rR$Q7vSY?gi$ccQZ(d&x9-8zIB<)Vh<B>Lk-tj*m*FGXg9`<Fq3N))0alx3yxsh(3woXmfqB+C33qRcJDMXx1L?Knk*8&qpmK<7Hyel0lpKJoEq}v|RFEq?iHO|zg)CCcFm?)$HO%pA`NsdNR6&gUxLXficYRySW69wENqYSwO2edg7LjJN*FB!qkU!GOb5e}KW6r?07GHf};N2fsS(R-S14tA{P@aNZ4k!uZ{JOMwE{QN8ldpc4TeWBK$u7W5<E=TZnYb#BAs%QBs%T7&IVPxC18!~ctWu>)Hc!6aXP*cH>*7HJR@^Yg-C!r5ZOb<_*r&%w|rJ@a?PIis1%LKYwf)7iXpd@!7rZHrR0NfGjvQW~=kr#+G4U9!boes8eIH99+;eZyil^%2WHTg|A*qh@ls&)_W`_YuNpS?=1wiC7;?XBvvBHXMbF+^!zS^z0>&4Y;3snjQh4wJ8UPK4`SP}LoTp&l*CD6AIMvB->5D%}sP#XQq2#)|DRCtN>{hYFH)32-s|qO(^k%b&74=&T#qE;(IIDfa5mj9(Rqm7Bl=FX1WQb{%<uQ0E70jo2X29`KRG@&*7wBe5PA6*@lb1MnZH9!!MsrZaHaEyub$n)PItI_-oZym{kcdP{pix0xX+ERqCsHC<%;R%{o=elmvQG-2qW=3{5A)W@BHpd53ku&b2t2sQ9pRlx)URb#j3_Z6yqEzJoL{n3LQp#dh(z!J4oRRKe<kmPIttc3#&vI=J#C$Fja@f02<V~cQAgd|U$$ss~gXr$ZWqXdCUNJUBv%5!<f(FMUEP2djovUJ9YIlh=Hh`;4KWR7$U#pIX(MdGkWmHM!lk+?t34U|L_0^!0lpyTR|qQ<V-GT|Fqmp;@)FnJBPWEn9uk$bP%s*kyA{(6b4CZXl25i|h)EIZ^1byBR$B^*|Am)J2JG`hUlDSU5&GsOWv?X8!r(WLZW`-@~SuCQ24seTVh+ko77@oW+sBLIhQMl@meH-{cT#;_xE;B!n`pP^rcqV?Gt{DgROz1s9J@hDT|pi~DlXT*b|`pZQrGf@FAIx#IqBatLq*j}in?6j*ymAjzkNujb4&EI2?h)%NM+?!5vP?}<>j%#~K7HgteEa-N<vH@lnxNm=~?gu&8s%Xm-vN0oCXSH3ip<rAtik4=Q>=`F`So!HRNtS~c)Z{dZo3Tcr@(v8`LAG%!-Bp1UMPNnU?4^Oz{ACG$QaMzcF@+<<+k>vUQ9~vM!WA!E%37#ZYZ9A8+a^}7E)tDcl{@5#qjpJ<f-#`3P_Fu205i2{GKIZs90Z?`BH{{qRS-oj^X>b8?jRBvZK=8YSB+O60RXE%8fBp1l?A|jmb~BTC^<1jm>oK{v~X)in-Uq_{V4<-Ww%5Zx6p&(g*h)~>crv5euvntw42o?ff15Ew>T{C@%Yay<723Eqig2cLL0T(fT&Q2mBCZnanyP}oSIsFY(+^zTc(LxM3*Xrs`px%V({KQ^C}zQK3y5nOA(Y&YEr9!*DpHh6(>pNTO}y6K@XIM9QZqu^Ia^D&9P3Fhm&KAny&(*^~}YuyqM;U(2N4S`&0-`aeuU8HA*CU0BcgoC`ml=&2jvj$eTIGe$PwyZ;&1JA_9~MdK6=L9SQI(IH~3&gZ)DdHkS;oMj(~XiQeD{<$Hw^tz*i%#+*Q4=Q-g;i8N^~r5)D&C2{O@j!K>f&t%B~^R5jGO%6zETS>}tida#5HtTmaJqmOhJc~g0&74*6Q7i69XC>Wwz82WpP~~rPKrD$5CWzUZ7Wyg^^a%HlZIeN$x1l;9wus{5%;D<FnJa1?3R+h|MNpPbLOo5Hbw{3M6cyS{*1VOj<<*fVa*cT(&YeX+Z6k6kMTeW`j+E2~3+Y@sX^kgmOSI%Z@y?}lKS1|4;7@P7obJN$1bVY_ivuSJhQytvLCZnYv=-RFJY0k~7-c>Uk>W+YxfB*1yLcHIg2hS0pELe_-;`YnxQYny@Z(Keh%AH7=o93sEBbsIgF@U)0w_7Me@fEQux$RO_!8m-^>uO#+I8^k@TF5B$IHgoTCBiLd)Wn!p}Bc6^nJsi=6Z`MXj4h~Ch2UzVfTW?b<Kb(b3oa(iORojW0O+ooz#Ku;QZLp?!ikd!`ZcbDfFa?={r#@CZ(u52U#Hxxb-`Q94HJ)UH5@ZZB&zn=|=Hz_t!32;IoGCBLn#`^v05+os2|~y%K4iuR}oY@EJ_$dF^^nEpno<J}UY4Y;yy15XM4h>jQHY@^#bN@qoq;PL~`8ZY|xf18P<_Y<vkYElk}cJQ+PIkPZr`ksCpT-i|Dz1Opaf<cb%YLgAz&gh$U}fqr1g^0)IBnV7J=Dv@#(tAGeI2FFX$-HQ%t4X*82WAmmYi5c9IZ~KL(g-m*IHJ=`v7w>@-V$@CmA_fpSrWb4)K%Bq`vy$Vld=KK<z-S%2tDb}H!FZm6DG$@n&#FW{FZp~cb3FjW#vI~K-xdWu%c#P^U<1tT<@mwC98<)gCiIA~z}DOphKJnl8BPrYwOFcQ?>foaU5TTtC;&WrGWLa5G_cb<2P#{@<5CqL`-uM<b(AREwIX~<CAHKasF#>qI+gtx`y;W>6R~BVvSiUR+GQTrw_DG9b!aQ=p=?cqAh)Y3Vrz^uqv{i?0{cv^tOiGeMN=wvOoQ36eV*IhYe#pDZXe-7KU{yAPFtZ+;e}Djfs2B%<Cf8CSna|=6$_<G4sk)%;5&Z2nVEQ3eY&GA{VJ_PTWvOQkV&lxfR$u0i^zRaBm5e`qLCB`buw}4v^3Ia2cP!hFe*FFPYe<h?&QF|+F1%v6Eum)XzWg>2YBSnRV#%*njG(DJ>Y#K4hQH;93Uz!<MVDdo+Pro1cLcq4Xf;V(G2R9%-r}c5Upp_SWI#<^CC*e!?8Rl#i*WG%P_VRnTm`EN3DWgS%Xw7+O;E4WVR|mp%+)xb@_6s)~AD|k_kl}HXVlHPF~I>0$seU<v3AIf|#b&SHg9K#(zgylGtVA1pbYwZoVp|HBkWyblYdkuCfb92r`m<C*GkXfjwqz96QAcyg3(A;Tg8&mP=_)wD@7qQsSjVG@W^t<&=2Fv1CRj{^&b7m-i*bkG6$}OGPLffkWsb>rVt;2$)2zKUH>-xZZC5YfU;|T~cs)ap#JqWt8)=HR(?3=QC=F<WL7%L^fqZt&1VmkwRU5k`mmvxcx>cf}D3{CAzt61xgy0-sEY+Bb&)*ab(~J=fW3H2e$MWC{y^Rgk_zJ1Rf@N%A}5%k*Vcc6|R5)usL@kjZ)EAF}TP%S)(ylUR;F;flu%}jnz0p_8fp;XDXQN;%!qT?J(o%0ZLmgDY$tUa(G4EMpQP@m<HcKI4E<d3raP4(UbGzlr_QJhygv^rZn8rrCQJ$veZPliTj-SSJhfN@=A1);LH*!En=ps@{uSvrpX1akfalvCt{ivCK5v=YOGZ~#ev0DOO%sLj#4`%#1&61icQ#4HUU@n1+m(aK$KOUL0jqzgTAB);WDDjG>pgz0`!8DrUV8rl_W(){nl2;c8Zm-!hCq5mX$u>tDB>IS}5F{9~!D~1%XwLtb${RRT3kYPZ1T~^6+a<rAm4ASWq&d@)D6~5%bhB%r#<y7}%eh^T2Pnybw2AFqg*3OD%MIE5H<qiF3LRm!YJSlWh0qP1-S_0D%nJ)42K)I>eAO20To?<7kqrb&l1dfSSkwy`l1D9L?df4EGUrIx6$N5g2IkfEA6TwQ=`~8s;tjE>b8})bgUvqpJ!BEd!Pr%B8&M)y~#o_ZL_;=y;qoiHVl@$={Zg2D^drCs9@Ac=d+>t4VRGnLuAj(1)F4t3HIxNtXkeY<j65!Ee1d#@aKKo&fYPe7es1Qj4@j>c^90MGh=;d)kAan6;P=|3x@dN{&hC>`=fsV%}i*jnUggGEoE`DzIBbX^7}s&RM}(J;K3o-dW=dS;4B{ZBl`1K=n^rHr!TLQ`AxB`=M4iie&!Ug}S3<mKLIua?E-t?|F9VpjucdchacO#rSr?;;rORszbypsc8v^<q!iPryA>lQ_?x_vl8fOSBRhQoWQ)fFt%lHG8#Q$+-1Rjjh+S^hoZWf3ZoEcG%pg)2e!%uByEx!2RdxXad{ehT%eWhEG<pjF3-KpJwrEDJhAkIYVF*E7)fMW^Nh@iOwFtA)xbJuJgD;w#my2O6g|D{+3K4`Kaja$$I11}qL#yjwnb-=q+fTX{plhhiX+h}Z6rYxW*(rg*`zFEgTbi9Y8D1$ZY2*AQ_fJi$@PRi?r$`?UPfUqcDw1CTs4|=PNF%8D^iU*GW0Col!04H*-bsAF0O_rC0eB=u@$E}dYQ^7o!3fABj*WBnNv)fCOw>sGud*uDj8~ImFg<hXqnPzf|wp8&+nop!$ox`C7pJl%zxzlnMG+F9(hp677$^+?l%hDuzrU@?NB)(pYwC)g0gdlpo;Wl-=9bOzOP7DyRDUOCRJNFo|Ob#L#c41Qm#CwKR61kY)%;iMl6bMOypV3e9A9Ln#Re~)f4WXXc=DgU9(hqi;{a1!eIgrz-kxu4cRN9m0PpQge$b~&Z3@01;4Fi)a4Txhj5NMcY3J@4OLb5pwCT{=Bx|FTwXOW=ArBV6~{E_s>}ZeDVpJlcvkTo=Pg`?U&39a|2enaT<lb-XCSHE#vH3y->O#EN|K__l-?oWs^xnbAxq$C6f#9S*j*gasRh8n6zdoRMdk~cvpvg(lN~a-Fg+i~Ncb(vy|5Z<6n>PGX$6{+mFbiw=eDvuL<Ao8(WrUI=pGyKIHYy!>R}GT3NfG~&?J#ityS&HX?YUTm5&ld?ILE7m=Ko-pI6TIL}J0s$&;u~MHK*<eQR}q`3i`gDe`U7NJ0$cq|qKlJeuf#TlJ38rKR#)>sd#NGIpZV%LU^ws+8BB^sAK=a~!i}Pr+?TipZX`LAgiCR7w<6jN=QG@nE)VvsiW7#X^xO7?VM4$62ftDvNg$)pnrRQM;O-66yvcpI{p%3W)NyqDh=yO6shv%gBAGCX7hMBcj8U%cUP3F-xGXY(|wo7=#IquZa2Nw6v+2m)|Sh55?^kU7b0uY?-5IeiTliEP-tZ!9uOF%j0O3>4h*o3<LIIag2(Y{pBpB+36)i)&$CQl_slz1NEpRioFoSt?HR2hrm{%2bb6<SEJG}X#%s%xCzo6`|4Dj^#$fF88wT3!ss?IVEVwym`jgqD$B_ndn#)iTX5-+QgWFC$u#+8|ByghxSiHjMVyT%`{nq-q|56<dC8C|vkn801*NuZ?FNqUP7|D&uSu%aP$4tK-Bgm45>LgNsBs!{R5CJi*2PS>_z0|WgO&It=jr62pe-}M?qeT{Vk)7imTKWcgG|D8YXUb?9VUtfou;XI0RmG&bT5p}m8B@L@J!;Vn7O*CDposp7j+(%m5P~7EjuZd4eWsysY0BRBc|3$5a(CO-tMD!Cz5ESbg7naOp{PqUaAd1U0F8vS&=;{)%uVp^~r*1xBj>0Pl_q`bUHQezPf6kSsG4~?>&I*E?7$2F>%QyLL1F5kHyKma+D&*@Cq3{Z%rxesP|p`DwuH#`FGh#k+MkOZKQDTOejx8jw+OfGM*}fJ2vx8sF&D<UJ>D~Ds@n$Q`fRNdjM9jK?Wnr9Bi#I0xC%|?I1|VhEYjsFy!c&2vl93DtQJ-PGfzHffSiuv0s0pmWJzhZB^QLWbFZaI}B_S6SlOayk)quGJVi#PD!RY12jq-8I#qY(1vKPY_=$mIER;g(F<sqNP5_GGIP>sYa-MEfrY|uP@HAJOWt3UcvHrKm`NBS98j^GXBgNx7=`n(Tpgk($~imwPEK=7OWImA<RHQzY=Q--|I8X-k`I?tWR*f6UQ>nhpkritR&T`bwge9;^DN8E%xPt`pv=P-;jPusJ+iK)$_H$zG*P<TBMi~UFFn4yowamU1J{+R%MVyJTA=Jhp79bBP6;)!M#P_28GRht)5WonwK#=!^;%7I2rUmRW0jWo?W>3;(PBZH^W_x?%}4vi774|Us^+qO#mt9;L^_05bklvwx~T<x5gcT7DJ-^r!IhR4CDH1rvM`7)H?SB*)YFU$lKI4S_=gmhl&N+WD^%F8Zov15Y`cv!P1!gU=WJc!(W!dJa7&35QpaTQD1^DRK|nW;g=u|BCSJ;P*%yoViiUEFo;d~f1l9rsYOP0h9QI7rq?TEEN712`3LtWxldYmUic-hdQCz2zsWU`cv%`^A&1uuBsM7KnIHfUAF2taRilkrFAx3IlQBI0P(W-0ydgtL~1uhdZOx18f1Kr3$kVIth5Kzx24<Tww&pFeOF3;$B%~HRt%6OkjkTa34q7*}5-jGcCdU*NLyy0Q5S4IU^Rs&eFPpJY)Nwx4m%5CVW6^jwcp3#;_DDM&{#0b%q%!}*0sH(iZ$YXu!=we?n)*c-^fhrd(*%kgIj(XL+*|9=-ToI2m&4uunaG&=O^;E7A&Dj~EaKqNwfj>=2eB3|Cac8jz{HoR7>~kr2^|ee_uL^e-s8dQm$r5dM2$kVO7ni8^c8sDSx_lV}sdZJV?Pw6`vP67iIT|g_r$>3z8nty<YgRR*xT$oZzZ|OeB=`;49wry5>vrnDbc(qx4da6fgYnvsQF+xwd%WV$6jh_ZMnM4&T2j;(Bq)kSEQ~`QEV`tQXC^?W6k<uv`Bjl>kqJ9xTEePaZ?S^95+&@A!;^wGdg`x>hjUzKV}Z$<e3xbtC2Q@xPHUufL0PbZu3eAdnW1lISyph;ZAj{E1Q~cyIZ~2syXh~Hx+ra{hI5u`GAryzA;+^<?vA$uU|wqNlc!lVIC0BPni)^6=H^42UCX%UhZjL<kDZH<E&!FpdLs<_Wm_hvT&~5okKp|!=GOW<m+xz(3Y!jp*L8gh7*-T@q4hL_j2NS$s%T|NsA$qatGusWz3oyu7a1N?8BCK;mUA|x_;bB-urCVZ7ONGMyS5(v&Mn0n26!yoSt}WApqE=w`KipDop<Q8L$9mdC)AzDxx<k}swL1>EK|*#+butHg_0mnzNt=1Gltd+OczLwS~R^46)_gwgT2|?KplQyyp)zQnA5g8Tdt*oQ}SVE!i+04!7{^>nh8n*28g+fphQEf)OTdNSV1%Jkr2|{#Nd`{(5$JNj#14M#F@Y}L{Q|kD15+SBR*!1`1h68g+^Y&6Xh;3|FqR`ziAJz`m&)l1xzM9-l7u>`?O9rv8F)47M1ks2$;LI^cOGc&_m`Us6uv9Vcf!zy)@PnxKuoywnX#VBU*ba3g64~W1FG*Xa`6v8*&042^9i5Yauh?;6z=uRZ*u8dBPU~3-7Xmw*bQJXfWwHQcAOQzpZwF!iI?YW3sWQL_=wjLwMU-h2ZKLmZ>YGs^|BXZqVrOII<p9+pN`F;F?juKcErlN<~r1``@bU@LH5UzmGZZ&`DFK!mRKHD?k#G{NJgjE9xyMw|uKu!adasG7b)$mz%s%tySZ-3BOC7Jxy7k8AA)RKpEYnk`@Wm%&fFdR=;N{rlsJV*E&_(J|T&CBA%AYlN^ppfI>@qNQ*5`ppfg2AM+Fv*&}>-nm2-^2I{VHnfI1|yL(iniR~oM9(M{`Js%f1+&vA$Qgh9_^tX>{*tXQFqmP#~k<!%eKFkOe&oP;W4_3qG*f&LJ+BAc8;N+fB8NP^ici{TE-eYnWGPNGlf32wKN&!%-)Orf7rZIdHZA;&d#7w2iCM?vT81!10De)n|VU&Aepv$;)&C?^f?J_@snEywPHg>MUq7O~$+%=|LGzbZdPbq=_q;wY!y#87?%H)aek!%eyu;qrl712kVxf}b+?Q1XpFui<xcl)8Im*J1R!pRK+`uH>$Tzzaa9h}g0N~4HNVDO}kBeMgpi4FdSOcNUp&}V5pa*AC0)^_N3-;n>BeWNaosG4P)KG`;Oxcz<qkNf`xM_OOm')).decode("utf-8")
)
_E279_DECISION_STEP = 168
_E279_STATE = {
    0: {"last_step": -1, "shops": (), "expert": None},
    1: {"last_step": -1, "shops": (), "expert": None},
}
_E279_PUBLIC_AGENT = agent
__version__ = "E279-V17-demand-dominance-MoE"


def _e279_step(obs):
    explicit = _get(obs, "step")
    if explicit is not None:
        return int(explicit or 0)
    return int(_get(obs, "day", 0) or 0) * 24 + int(_get(obs, "hour", 0) or 0)


def _e279_shops(obs):
    town = _get(obs, "town", {}) or {}
    return tuple(str(value) for value in (_get(town, "unlocked_shops", []) or []))


def _e279_selected_expert(obs):
    seat = _seat(obs)
    step = _e279_step(obs)
    state = _E279_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "shops": (), "expert": None}
        _E279_STATE[seat] = state
    state["last_step"] = step
    if step <= _E279_DECISION_STEP:
        state["shops"] = _e279_shops(obs)
    if state.get("expert") is None and step >= _E279_DECISION_STEP:
        shops = tuple(state.get("shops") or ())
        dominated = (
            len(shops) >= 2
            and shops[0] == "ICE_CREAM_SHOP"
            and shops[1] == "YARN_STORE"
        )
        state["expert"] = (
            "high" if "YARN_STORE" in shops and not dominated else "low"
        )
    return str(state.get("expert") or "low")


def agent(obs, configuration=None):
    del configuration
    global _ACTIONS
    expert = _e279_selected_expert(obs)
    _ACTIONS = _E279_HIGH_ACTIONS if expert == "high" else _E279_LOW_ACTIONS
    return _E279_PUBLIC_AGENT(obs)


# --- E283 deployment-only raw-loader entry-point repair ---
_E283_LOGIC_AGENT = agent

def kaggriculture_e283_agent(obs):
    return _E283_LOGIC_AGENT(obs)

agent = kaggriculture_e283_agent
