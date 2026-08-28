"""Frontier V113 with all five route slots corpus-screened.

Base: prvsiyan/kaggriculture-frontier-the-moon-counts-melons.
Only the five route blobs differ; selector and every guard untouched.

  _ACTIONS_10C4S_3Q            <- episode 94469751 (135,608)
  _ACTIONS_8C6S_3Q             <- episode 94368369 (111,026)
  _ACTIONS_6C8S_3Q             <- episode 93908934 (105,384)
  _ACTIONS_6C12S_4Q_*          <- episode 94369942 (103,100)

Each slot names a FARM COMPOSITION, and the feed/room guards act on the farm
that route builds, so candidates were restricted to episodes building that exact
composition -- a mismatched route costs ~-100k. Within each slot, candidates
were sampled across the reward range and screened on seeds that actually reach
that bucket, because episode reward is anti-predictive: every winning route here
is mid-reward, and the corpus's best 10C4S episode (160,658) lost at -5,166.

Measured vs the unmodified base, paired seats, both orders, FRESH seeds 9000+:
  ALL                    22-6  (78.6%)  +1,266
  10c4s_3q               11-4  (73.3%)    +851
  6c12s_4q_second_yarn    4-0  (100%)   +4,672
  8c6s_3q                 2-0  (100%)   +1,819
  6c8s_3q                 4-1  (80.0%)    -328

Coupling check vs neutral v14: +77,242 against the base's +76,826, so roughly
+416 is absolute strength and the rest is share capture from base-family
opponents. Never worse; the gain is largest against the population we face.
"""
import base64
import copy
import json
import math
import zlib


_ACTIONS_10C4S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<%Whm*a{L#rxe$wQ@7Pk!NEmigprk2`8$_c4k72+VFWTN2{&&k{J#O6-85xo1REgczN`+$S-t#`0k&%%<|M$ti{`%WL{{Gv^KmC02!<P^D?|%7s_v!PO$K}b>>B+zS`XB%DpI`s-_2WN&{q5iX{$F1||9tZP!}DLY4?leQ+b?%NefaV2{^a!J?ZfKibkThM>HTu~aq@>x%jLVTU$5RT?>?WLUeCV%ae4pn)5+=C_U9iTAKra=`+4_2uAZL$=XBb!k00Lt<;%z2o6aVE`}t(G{Pg*`tv@|Het!S_Y5Ude!~Q^gTHfF9-g-WN>*jHjSAm91U%UG>p9<7~+3UjDgFW1~<atic_WHX16?xak`@6TxXgpDWHva*<ZPsq`*7bjxj%U-3=kI>nErz|mu4gLvSvtbYyZQTf%j53z@^QY1=HKnF9=LQD^F{RO;mdpxwTtsl|F<*tzM1uoO=UYc`vW{1rCtBt-mRDB=0`6(bJBHdE_cJ#zH~DR(_f|21@<4B9Iz9b6-?f;9(yomli_G)to@BXW9xCJL$~+b`Oe!7VLMI1x;zsOH?SGPqm`d6dtJ~*79BeI<ZW82kEQ%gK967s*Cz~^qio*vLEOG$`{C=^`w4yU25vX*Jr7?0l1}>A=hF!v(t*wYoxEx2bJGvs;IXq?<vg$^lf%@wK*l_EezrQ>_vkH{+au(sjTtef1#chj@0V{s|MI8h<L3|eAO3m&Oc*qH<(C*sr2LKp&B5l@p0p?2Lt95=_T%6xzkD(*z*oKgjrpDT@uKeCruJW_O#;lj#(bO@;b7rb{0v}>z&(L`wO-nmnaukz?QPb_bO3>4Zy2P^Re_(f2ePq1pV9|1k3h5^JN(hO$wdb$9#qNpRW=ay&GY#uo=%_Zs{l{w<Dj=}I1j+M-#xN52J_9|0w=__%-d%@E;UsNZgynD`uo$yKTW>(fem$m0qnCbqW}TPqN%|yw!SNlp*g|roLUEkYcMkeI-xr0Vi;l|Ae=G0G>Ug41J`%Qb>FCfmpPB7#sYXtH2>+1pxF>5^Mni!x7zYYQ-B)4X%+xTa4tF`Lk?)TN{62Ob1dzTgPeVT?Dxl-m{e@Ns3Cd~L!bX-9+gilt;@=pS@Fe9aHQz+8DL0X^f0r#Dh7%NDLL&YA@N=>l-=pU*u1}c{A<*)UchM59o^LzL(pibwtXoM(R3_&_yO(Uv;o8|6QBzP;e)>I*vnf@X9n0K+d-L*RE}i;aAa@U?bhgKP<G);dC+%HM3>6+eRKQDiVklG7WC!<Z>WTa+Xuh<@aF?uv@LV$yV>#oDA0VFnMmv3-8}F1)@r)cF`v+wT3bq=K0n^Aepo&}{tb`=rLYmZ!(fMkx1T-rAR&2(X}={yVoNLiMD}ecJ$#mqn_(Bu(W`z$$p~VwnA7S|Hq+GHm?BgjWW-}xUF&1}VS7jCkJC`t%@sS@hM0;vF!0#rZp=rZxC)|vTVKC4vufg@PcIFv1U%b&i_p&m=Ct#;3e0yfa@_YY)3*v*T{*DN<q<8F7(8fq+WJ*rH{#<1%9b#3cEvrW-ggGCRPGgqKTK}H)x*R6bCwD;qSk+0&(PNc@|_R}+_~abw64q^I)#(k9G;AuFo-NNAJpgqkd4^Q<j6x_L(YJq1CoA5-}0kFU?lIQa@k6tP*?m^cRc!tMs3(P#jPYPwfR&=AD4xwB4{E2F?XLTSRKOrCiEj<F?MeSV+7hcM<?3+Y^dx7HrD8qIWpk<X@T8&=($Ft0<Oi(N<EY@bX7?~wewpc;sT>)7rAi-Q$%fx>oAO>%x2mxmxi&k?TvRBpaf4hFjk{gwlf1FK&d$ye4UwV941gt5a6BXS-+>{glIWim!u+Q?37u`t7j>qG+?^kc~-BCDG2cEHW&rl(;5>h>}cKPyD*+bo-(b|_Py<~A<ji#q}?*NaqHMUuN#ZubsIFqxRt>sY>xnP?}HZ2{#HzIWi~<jq2wTf{)U|@c9_g@rJKG{N2Ysv=pj>`QtSfsHnZKBjk$eI3Rrq<zjg?=XX`v;;dD?85_EH?jUdORYwrf@U4Cpan**2?hkj*G@VNR)F)K3mJIdU<+k|^(Da}mzeC>?`e`a|Ug<J?~>}>zo!?>%F;<lT1isMFx{pPnq7&X%o60Lbk2gUZm=B=19REmy!&>=V)cgOMiV*c^N{a@BAFLH<4U*;)uJ*fA3OTWDDY$194XYPc7C1gAQ+*Mijqfmr!3l<#M*@761<yM+;A|X|?BHxrBz&p<6)QoDtjFy_|Ia;+L+fLZ@V94p5r%7(E5C&{k+(nLiwycVYwih-{ktfx*5+93wfH;_U;7YJf1eD3z2NdI<Eh!Z^CL;b3dn-A?)kBM0+nKp(j#pR1DZrS4c`SUWCS_B9@ffXR2VhL%E<z4UgWy1*jR3B!>`XcM#I`4K&?IR<<?eK0cgD0?AVV1nA;StF2ZnH*QrMyb6m_LK3e5!{iV#kx=biJ%%v?@48ko?%S%9$Y@e1zvMRfO*-)Wjphw#&ZwUW8%gktN3E_JUx55_gdkLJ7&b>m@b4>n0<hgSY!Z@MCL=i4>BL)_byG_EJ*B+q^3*acoxz{UdZ(K3vC(?BZ?0~2=IMF<@V{`>So-S2;yM#y7xN>q(@*0431D2C`*ONT=xeH9#3>|F`GDfr=II0Ka5#FVvK-~()iN;<RTbhlnKFjdKx90YGj$xwHKR}20oiiPOp?1-<xl7}P@7?^sXi}9~I^OKde(3+)6V6rt>>-0Xp%@5sTdkKgfg<j_%m&p*qk&sE+7eP$hRS~^ALbHGgH{_Ma9Id0Z>Xi=G@Sy(~y_(UyfLg2M#6B5Hun57xFF$*-X*x#?*O%Me6~?cNsG031cDNJfr>3H*p%bjoYqd+Jz_HRzd6Fu`Q>|CTs;|<l4GO!<F6~}?8qK*q0<hSOBM4qwVvtLcIR0^7K<H-qO{KB-xCLsGV3vQ{(Q*kQ0K++bw-~}su!{lb4t*nQA*3Lz%(1<7$v05_Npt>b=-ge-S5G=EAG|o5e%eIvpYuf_oZC`N5H|yAqJ?T;d26R}pQ!!?xp)|Bo3GpU8!%~N`*BjqS=+TM<Ah<Wm~leDyzp#Caayh%B+{f5G&(eUH6%x^uf2yRoukZnv5{~%1Ph{#PSY-^>+!Pf_99=83;~}F#8oo6D|Uzg!nZu5SHdBp;pX5rF=r7k4zgU+Ded+2fR~EenA%oRK~8nW<`S+Ty^YPsO0%oN9;hy#fW8tI2HrO<OOhNZtjK3*IOmJ4uU{TUT7;5OBRhbi_}G{**GW41i`dJc6!b+oO@xC{-w=b6Qc0rH$remdB&(DGoR*F_fI%SSpNrI%8bAn21zV^T14iTw`lcwx2tQrsvvjA}c+cI_NtuP*NuBL+tJY>OfR&i`t-3;qr^<mB2Gvm+C`0y8uoiCA^F@NhQX~|(>LifPa|Ozn6Y*dX!CXnH*T^0b!*6cUl#l#fs{z?e$^oJKsj=?tHP{K-H|_wE{W$m<>zFdK^r+Lu)*gp2j<@*Qj6JsYJoQ%YE@f#6{W4a&(4(9^;i}KD?I|xq-C^Y$KxrML=@G?Cb`h1jw2DhoQ0NyxlX1UGw{6lDDpZ#(G|+mA4k<NMs;OcWIt4FQ7E}8hN2ZXh67jg?l7Z;21DA?YBA4qI#$VHWhJH0{<<NjBVAF{}bxqNd4lNC2<XRxX&xhPn!}Uufm`solx1p^aj@46gteQ3z!&BQYr|r2((5%BNoB({v&G=u|)u*=i63UTsSWq&GWY*J2lA&s3CK4iQW41LVDL?zIUzgj-7t%c$urewNJQ*BU(Z^$)9VSs>V4kv4^=*l*MzJB5I5Gc9Q2jU3Omtoy_csQKlLI?iPAF68an_=1;S16EVy><@iHiysh>Ax_xvZ5rL;hG=##zl3!>)C08fiE;qoXPEL{;yRMWdOQ&U`I5hU2I`(SeMMW2z~B)nTOW2B_?q_`ObDDdsGt{+tBxDjuGo3Luo&q9Ba;o#@g9D^Wv~Xxr<aXSmA!EyP;rc=;L;@*wRkPjg|(8WpI*V)X$K!EmDSLL;qb{F1(Y&3xrKsqFXSK7Vt%N9#mGLbsN&&ai;az<BGY?EX}w2FTVGJ9}T&=2<=YOG;YFl=c8(cbL2iux_@eL+0*Qr7%j&jiIazviQ&(@b5VPuaB=lh#8tfPfj38of9{4<J=)#q%TFPk!dX{RY#>7<py?W`?m~jF|w-)LZ)z~GNy-}#?vDKsugzNpQNcS%&D`gJPzd$$qt%DNF9>+XPuMC)o_^yC6TBr{B;Cn&@oAw5S{hql)WTgFkxm`e@%>yi!gn@5J-!X9TWj#-!Y@3%TOSq3nLL&X8+B<3AHG4UiTO;il}=d;`FPfDxl-)?^I-9J6i*ITz<1!hrCxoho)*|88jpFNt6#0Dz8$VTWe$uTDT3YX^?k!_U(WKo+g5J>JdPK-I7H@fg$wKRU#L7VQush<`8EgZtJe=4W<v!*;HnzTYzM>tVwBJJ$11tnBP_&Fr`ACUX~`siwu9hq{K<RunjqUZ;!uu8QS$XT_IE@e?WI($yq@P3k=K<U@2fK!Qs$iJR~$-n$uq06fu2Z+`Nh2KCL2AaS*{2!3#!VA+x(qt!t#F+=PCXS=$6JN9;sO^`r6{x5Q{S$`Dt8yoD1SS4a&Ea;#E@mvG;c7u)g7bA!TQ%=x%6pil=P*N47-(fpg*z|+a#c}Q+ni{fM#^nPk=@ewiHNhITU5t%hTtbSs%8h}NsKk>W<)rB}f3|1=1mmB&j{h55o23xokjZ#GdBO1iC>I`#uZ&fr8ocaO^Te@9J`!y<G6i|!_nb`UoeK{>yiEP(5hVj}<ZJ#a#eEa7SsESi6xh`OpvS1x15{iCfYQtPRbkY3Cl6)b`rluWByL0noP`+tUkNS<NS?kNv3ELy_v9!t}D^WjH_1@n!tg}U*tfXfYYW>c;;mF0Q39VpNVf$0O5yh5kjC8i-VSB7x;k?;bMh<#H_SBMc69EU2!Xo&5ih5}FM||j$GiPwiHO6{!`cM*rBSJclFjd@cEkz|!n(iP!qn?~g1=?)+O=8=m5|(57(VqC?)|5~xmZLzUxYh1xqyk3xC149V{D<idFZx9@<U(Ld+7Qp)sV~IKdMd}e4}X4s`{rL3eW#57%>yDr#z8w~!%lm!?)1e|Ima8UCb{3l+t(WSuO$qO3H8^#gfT(>%#qfk@P~=~>s2zkD5!qWKW#-X5>%MqRyb>r1ZO870QmoD(8b8w)*}6SARXP<^qMV%^;uxNnq>o}`zwKbRUZ>o)RW^u3ac5sV1MCArpADJf~@4OrsBv{6S{FvK@wZ}&&mQ~^-YOWl@wBOWS|rnfQn}l_ooutm&{l@N|MKQrC4&?S7>oi%5^92RZEOlgxe@CTnz$i@o`NbVwffaqkl`K7&JD1y2wB~_#`X^$<#QmK4P4RM5_zD<?54#X{2PUA-Z&jBzj*39-yhNR@aKwoj$;#9!EwPNB{?fU74joF0KRU|1+gFYVznB`X23KSb8|T6!kB8&@VOkI{eY>?}Go1g9`l#=PbAX&7f768OGqmm#G74eC;eOJ9S$LeHJYE$S2CW3YYENh*sdpl0#0z{bFK(<Pg@Xjw-mn;_2_VPj}#W((K?F)A;=~K&lp^>IuT%Jay%_FQqbxnx<a4$zJ}uSe69+2g)rU6Idlkg(`j!uxA*~G9<LhPHp2j6UiuQa11@Jr*P$Ua|4|j<Qtj<5+HJvztC>Q$$yrVP6H$M+DcHjYb(gCyD_tNRSo+~B8^CZT=AL1sVYa!HGYYfClangy0=CgAoY+r_azvdiir)+9N(!|ewF%&S!bK4WmFqh-eIM5cBvjKWEk^4Ui40rL`fmtiwGYTVjLTDDT~MIg2|3Ew+m580OAa-3Pt-3AZo;i{jqSg#YJ55mh8S)l;*Q|J@pGn;T};pP5=Xk<n&l@j1dv0l|YM$J+kJ*ss7*lrTC9g_+X_Lap={1=t=G=C<Ms5c(h-gbrLdh2<knhkZe*CcVPVl^eMukN;_F9YCS!XZ%cI+n9qPm)|dp*rm?beM4F0NB6TR&Un$vu^SlyUH=l^<XUkJ7W#jN76H>xaSeo7esjiKz9C1PH>FzZx6Ly5XjIKq~*iQIDJw|2_K}ZV;U(oeG?Jh;ZcQ(#}QRgpaZXF8gP+>r!n5U_q(9y4p`ZQ7ugC-Nv1Quvp)>1qaD5rI_wR*Y?!>*Sn7!FmnCqK=p=_m~`yn_z$hIXaN&N%W+<sG3BLZRAe2GaMGN~!i~XhE0Pu$5S?5L(=m_Z5M>>kMl;3gplSkK)s3BVK!NxS***`|iv)1H5)u$pH$CbWy|-^)!~T3Q@fC;h<N>U6T<3=w`~uMBwWyas<p;OMPF%WtQnVKD+9)DnOZd6m^B1V!@a&cATHyx5nzNlogey4_WNSIz|)u28H?!(}AIFf}RPh$(|r^)c#Jk>&6SwS23^yMD2e~4+Un-2*$+oKD`tsk)61O3b>q9rU6gNDI1DB-PA|`67f-`b#P;=M%;Lw&>LYwy~RpNU#ijQqzjh$f~aID)z+YUjy^-Z>u=*lm|MAon2XN3l(DaQpS~=VMEX*cFQqiT=$428C_0hB0`$stK{1O;KIcjyf~xgmDwN#HWx%u1h%yhYkxWYu8+dkmFDOu<Ru_>aapv`@suQ!8<<F<;0C}PsFR{J3htR5%MC-WK8$3-a<YmnXLSb?!-poxPJtNF2I-hzRML)*alFI07K#!-TPTAr+^`MrNLrUrgDV#7==Vw^dpdv`7Rru2C6s6tHNN(qYNN(qE0xnzVA6&jxji94TSL1+Yr7}=zRt_M#Ww=HPn;Fimp<&ICJjw+bQf{}qT5_%;?^P2{+i7@@I<afK&Ji%$_uURN=PqSpa&taHu1cXiyBM$|xSo}`slda`P>q~HjX6`($^i^F4r?W;CRtk*(HsVHF(@|5vC=rUJ`#In+*Fe9p>9#?YU`fNbp`Tw@)K$E62V))^#p^WNx85UG?|aljPyMC63E0vbfqPOw`B>VS9xm06Qkh*4i)hPw?bUy;;F#T=2{lfcA(%WI>z$WUkc{EdH_;BNN~7@`?{=PPQk8B16~wJW>g@Xmn|iyg3P%jOBQ{K?gIn4I5stvAVF*vHXNQ!g%@K=<4{Ra^?B~+&l;-(fa&24C9fMU(@n~G?aX1-DP59KoXewAL@Ctd#IV>#XL)gv%o#F`TRv_GX%(uT^s&!wWcJz3t17hi%D^dJSB*;AQXqLO`;4WnpihLuq9ng1d6i1)r-6(`)`{}Dpe;%acbz-s!C>IjEHN2^TH1<s6I@MxGOnd;RZ^?EbZV!yuF5hISEd2sQsQWQ=5`lSgLhQ}1z{r_xH0lxEo7^)e5Yvhwx?QF%DSuk`$*P>U7tqacL`dI^;{=Tq9OTsDJDcyo`5Nso{<B{mbXSGs79wuFdB5>9$;lUNur4zlNJ3FiEi%FOes-O;Fc^=Z3gqbD1nWGcx>m!3Y9HVSHGXDLXVf9Bek+<{3yBM#M(?l=g$$xnx=DNVJik-dsLpz+^|F>>#9^mizd&f_e)Y%N1fG6e){yupNaJX8Rt)fO2^z93;_hw))3#65AYts8(`=Xy>>OlFml&2w!R+6j}LnPsS!~*iW2Pa+yS%Aq5-BdhT6OH8kUztyv5Q8A(BbJgb@m9A&9phKm9`$m>bU?+dEW3O}AY7@96Zg)cbM3HH}H80ug13S*5bw>*kRiK!g8VaLUpW@1pBqRQz(OVXBmILj5*c=uyE8q9JpzDq{ZQ`C%Tpm1Z8M!)y}8B(H(j(zSSOMLHP$DjPlSwhZEX1qe9i0W#g(fZ@_b>`I6zsm>M0P1AyVjK<|k(5NK>dlc2Lg}e+5=#r37);Nmi;{UvH5Pb~yrkq>D68G6xJn0xXdvMJb!u@IiI!d-n3JMR(2fr+(-SQG72nLw&hN$S6PM0i1uIRjMR<@G1MWR^6M6jMv!KHwMaDhR^0Dzlc0cOidX&1E&Pck`_JFKCZ_2Aq>JOI`G)^=fw-Z9gK(|J2&O*;e$S4%0eyCr7{@E*zwoe#!Pcy1xm*^WgDLvl2W@2oJ16~?(&P9e)tv@jawqd-jto)uFPs}!-6vVOSwls+BoTgZtW05sr~oNh{6hm^>9DUC>iiG+zsN@bBgOf-}%37D&5y|!k-%4HpL!GBI48zZACdaH1u2EIX_a%uxKqCde3P%8Nk30+4(87oRK3qhTZFcrgT(s`xPQcPT4TWBQ@geW<2%(at?^0Dd^gLo=eU5RrP+}268y^?f8>s)g6N0DBXR9mPQ7?fq1TI-8hgS>{RB)VHw!%VofOo=|(`l(%*l}M;%a|(ge_OuSEUlg^Bz4?R_SjwfdnKguA0#=@th0EY5vV*@>{Yzd7Vku<E8JcQEJg~cy86ZuABg`z1Sy<z9BrofLlz=P2rRnhJywcE7U%7=!Xt-R6h2W!>x?F*zx~Oy_3w4=whYQWVI27!cG0XlCxZlysZ%#u_AuPlMgJPtzk4%Q#;gwGlt5!o)3vD`SpDWR_<E`(kuc_Tn-2=?di%k%;P(c$cS7WdlL0KbzD83|E#MDjzE+;s~EBr>O7G`@9r#dk_ik7odwAz*=l36RxVWm+^RV<AIhkDt9ZC|M;sLB{&t3epWoSX_D!lmcI9?!MtxNdZ1MJD-=U~gvwN__}+tha_aC2{3~?s}4{!8L<dCV*%}aU48`Ay8*si|Hm6Zgb|fQbw7rCfyKQ;7DsKUUI<@X`s6pZeY*lP!?etY1L7mUDHCQ4j*&EjbdaQCON1vQwrc65sKo#Z_BIEuazwAtnTbXnX^+#8XFv}h%lh@*77Os5coV(nNy4(=91n3J(LFWN=k<sV$gOgQ;($QU$`QbB23zHRccN4u%B)z`Ds06r;D(n+-p+Fdc9>EJ9M%Fq4z;(iBF7j6y8^vDpP;$#nrgNiwrz2FrxNDn};GraqgFcoph8(lnGEeJHN!6xvfy2q;R%g_7U9)3opSNqtgqWi=i=~!lHVl91cPLirhPo^gSejr(FX{S>4Pl?;~iGs8AYV&k&Fr)0-;&Nh@xZNcEReTP)5@o1mo7o^(7<P4DY*0b1tFb*c7TLO4OW1|$;7SY3TF{EM>7)86T-3NrKV_8cR8Rg~tkd5S1>Jwgs{I%yjhKP!&O&#MOh8pO|3>yo|nf(B`FooY&B2+#7ql&IV~Am9xmN--FR?C1=??m3{5vRIj*qU0nh_zgP;AoMXpW9>WwK6>Qk+ItD4!?C2YjL=%Iy{Yf$^K?f`Hx!tzc=0D8h@K^XK6HQ6pcmQPbov|TuD-Wxa{S6p7V<M??f#x_UXUGH*YGDtb-RUmhJ`z?=JbtD+1w*_?G65IglFp5UytMc2dF>^5CMovo_Ca=JRsAntIlLGm9s?dI%avvVParXVP{dH>@d<^Oa@-n)vnG?O$4aS0~4}SDkLziX!c4i2av!xVmhL=f<11SzFbLSm$hmcF^m~8^9p$l|CULJ)beJt>XhiG3DBx&k1@g@<}I~H6*XD~^u{At(VdD&O<Ei}QHANtR-uNkl59$|{qif7j-s6*D%Y7U-1UjZE{*Bh=^?~%4E-Y_CCJIQtm>xbG^O0*8bV7eu!+L<)bk|{q|lACx+)Qxnj}0D9lCTJDD!LB3^2f-*o}$?^@#Cr4KMYKF>bsDC2k==d-NsN9o~gJ)lw9eEzyj(qEU%TNMzIKB}9cSdVUN_)kP>&(ncD8SL#tvY^JCE>$UN1YYooiXLQ8?yXc@SC!3p_?Z_Rh(qLk;7fgA`gC0_0(CK<FU*!dNbV?Ept1BpJJ<vwyMQT_&izh|Rx!$_8w-O5Kk}cQqAyJM-N@6@Ku`hO~kiaM;#7^$773O9Z2B>5h(o`LWFJmu{RVX9#a@n`OA`RcrAXdvENs60=g~W>3IZj0i!xzFwXNGzV74i{ssqo!h8tf!-kufbrhfb(GXf>IbI|*Ga=U=<^l`9pwGGmJ_300lG&{XO;Lv{%kKJs(#q};L8r>Q9$X%tS?5k-UYqRcTLi#&k*rnd$fNNJN4eTZ(Hct8qe=@fk=N-Actya=$gTFs!0uEK{6i>2i~)W(@fu4&>pnn-xgDzci*N(-@C6uj6St!`Ur<!~jRC}Hhv0bG8b@3t{PE-MH}dnW1t4PaaBoV77L5Cwpdb0b8Jf7lS7`0p3>&HXk;zJ!j;g>&D@q8{lF*g*FvcW0oAp33FR)pim(Xez&mW#<kpTm<K?jh|(_B^eM|PJFrow4i=Pu_ZI2b4`u*Mr9&Rko`dGT{`54OsuO7+)si*o1N6UN-RCqo3-Q^1`Xsmf+KBXhW(NTuB38r?p*0r_>%14#Hk&i0HkXUth{MUa|`K2CN;y+pw7gB#Hxa6Gt&v?dfNF|Q_hArqDzOxrxHYI#+21QktLpx4Yc&k+GHmswvx*-UzHPQYZHoo`Ov>4w+~D*UuG}fM>U$i6<XKY@om$h7o7$%`a?G?9|G&csAi4*V6|!<385~uUbX5<NfO-^6`Z-k7ZtxUv8H4#^0H$~>)T1ES{m8xF;H@_d`v?WjyZ?XB)v>`D0uXd$>B>C!wkiJXChd}qd<+K3xdZ+bks9%M|<>%B?ET{x1ciD+W<T-Z4=_fQftAgx&7L2vQ{cC47q@Sy~0KyjMmoP4lMxqWyV=8v|>f3ytQML6U=%&h`F*^Ve*j$K~bm>5%*r8MtDWNwXz&wO~%Kx)&Dr?ekzt*>gzvCv(e}$PX8I}MY2m+|KB}6d=#Rf3y1Ud^31MLAtrHa!6tGhP21P)<M}t+PLL0isMzMKwBdWjzjYfs(qw3lCeS)^Lv26IdZ2XWJkUaIeV3>I1@ERby#')).decode('utf-8'))
_ACTIONS_8C6S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<%Z?mLa{QM**Marwhi*M&tw?OoG|?ngSPdG30knbuVRabkCg|VAWxX;pEX>V3qN<w<o>-_ZX2v_*&CSh!{okv9|NW1@{q>KlfBN<6r!OBK-u?FR{?q3#Pn)af+0}pi{$Kz0-(Uao_2b`u|KmUZ`afSk|9bWQ!?(X`AAb7sm*4Jx`SA1o!`1BS?c?@pwkW>-^nSDXIQYY-&F0<Luea|v_n)t3H<Pb_-aI`1ay6SDfBy05@!glVpHKhe`uX|)X2Xts{P6bAUp}7RG#~Ws*Q@R3)8}t({pIoL^ZRd~j$chaj0fV==HcP=*5&lAhsO<G1sXDZ?dj8WDo_I^udB`;?BTH`-{xdK>g)bj<Xs;h?%!@|<B9rn_z&Q1lXjE0?*GehJd1XG`|g+1Vi@&xKU0;Tg(JMVpT7UJJnlblo~Dav`rUZ-z@@vGE}~D5U#5$wT%3RU`_34BGwB_h%5reV13Vd}Q~%!H@0aG`N4uRl=(;tRr{OAJdKiV_ufpj9`wvYH*a^i7CU4n~Js7jWa1=9E{zjj%{kYSi8$EZr^G-upPE%!F&V|DbY=-L5%FmWj7qpQ@hfX|shnDJNDSs2sBN)Q{2?ORRnm2tAkMB5s_<Ht!LLa<=JB@qGgZICrliv6Fbi%uI;P8J3Z|eHo@WTr{c5<sME7oLim>Q=b`|0Du!{+Vh-~P0D`uySH!@rJKu5n3yKP@lLmhY$OQ!DF*n^PEI#%AjD)BO!TX!>kb_0INA$>hhCYkmD}Sc8{eZf6?LNgr2vPdBs$8|@Qd>J_Hsz#s=}JmYf!!vt<0+^hYDu}o&(hhcA{K86DboP5JLWo`@n6g`lQ1^N^|ka-89E!p6k)|;Gkrs{(#*}=*NqJDZj|HSKQbAuHSDtsLDoDD|;82YD2mWE-x`AZOm*qL$rtjC3BE5Xn%Y-Im<TK}iX_dc_s#$fim$tXaevS@0si>>X7W5`bBb`GtB#5EWh0*$bpbTM=>5D?~Ay)=?{BLmt`$93DNfR{Osrp5wzOKtwc8$q)nQsxO69&WY8kEUQXfYvN9kYHYPM7kW%aFupF`KP$rKMsoa<FP*;Yr<D`>&1@SgTQ(vLLXRK>&%&%@x@JWB<b=QU`SgeF|xZd28stMIqfIm@m4RC-RYIFd4K=(FSU-f0!D-G=&rsPjz&Xu>`QWphGWsf6(|R%3??2~0Zk|fAM|6#c5gME8DNhb2W2=?F_r<qk<qd{t<l4voI;oKpr4+IE|uZ?ruLN;DL#-b=*<P*kO>u+4=(vmKMaH)k8MSG){%|0|K07k?OvKqYaR5d8c};w>C@+@`|VGgr>DOFrl1rzVwV`~Q049O=N2d=jxmi}(j~aG)sJM~h|=R{;kX%w;S|1Vhm?#c1`9fE&t)_X?TsNs<zYrVnANmCjvtPfbo@9ChCSS|gKda;sU0JaP5#Do1d^+u)^F?UT{E*b9{RLvXeQ!W-dlu=CeWyz$7OK7voYm<#F<_yYIW`4KI;owDs}Xr+-dt)ecgypk0^D*1lkq<n7ZE)zLL3D7yvQ21-Fln58qN&pb@qI<9>#|9+2;ZNZ`pAx59O4`p^tcYQZgI<b+Oak?Ek;E&$nxJxq=~<T>aJ7&;&WsP`@3I|fFQU^17jgbFnUP<6+njcHWIeM8_%0#l1mY4~xI2rGgn0u=M~DFfCa&~Ly$0v2QQRxn1OoO5)dP0xnRUSMO5KA9r}&Yu$5oyMMXJSyN?Osv#%8AI2Zd{jGV1`!t+He1EU70eg4Ew1xWiXxlov|I|x&apS%VSutd-N;yuS6R*s2myuWWaaC~T;ni-dV&D&JWc_grL&{u)LoL77|~NE`LCX(h;oAIdgm#=GNvHFug7Q<Y)@%SsIa4Tm!INz7JJIHPRsX}$A&l;ZJ~C{+{UeA_q=W_R<GMiLyTJ)Y{K#gAoo6K(d2K*Y*%Izgdb84BIs|mQ^^jKInH#`H|ofA4-Y+Ls#A_#1-*@IH)dlVUlRhB9^J1Tg5%jbO<9<Aia~;Io`e$QaCh$AV7<$aO{Q}Iv*O&ZYzZD`Un!<V*8Prl^4%TwA}raNA&;-Tap2D^k0Ox_L5-c`A6qDQIab_p(++XmnqhzVtq?|yM1@47k@7*YeQ<ayrVOQ`;~sPfj>gk*yuX-#{_ybU{mQGkL**~yoVga%d%vZ3@0%~;ow{IHfIXF9aoMl{cVhGzB$QjQ;=tAxq+u+-(hL*{$(rXBa{@>6iH<omunL%?WNmsbSZ*wjGdVmmVy5RTNZS<xgvD4cV??y%TMQ(?u+fTqtg@B(z-)uc!Mp<}gY7OLU{*dL85u44s=#Ftk&(I|6LViZ9J#crnFHtedpQIHj2W26#D{FYHuWSg(K>bj*7@B@FhXe%90;@#z+D!dDQBP9@+7V_Ng7bIJGm`k%$kKhWHFL=AO2ZZM+5XH0$^kyqi8jH?k&S<{QuF)@HYUR<|NPNC}D+74FZR0Pgro%SGAj;{4VU@vZ>X?e+RZo<h~Q?trybNz4<suSC~GUQ{Up=7mfnV`N0OM?C8orY|Ue2ZhpCjPe^>ZlKS-|o&7mxl&$ch0u~l<jyBbJI1Rwk@GxPmtq495y7j~Rblm?my^zQ3lxQ36tYK*~wG7d%mJWwZUMo1L*t-JQQ}Dw3a0w{yiAipium{)-nLKC7<t}|_V5yQV*$Lc`lBDhhpBDU0R1wih+cij<B^62jFEI5$7wf-jOkCc%0-8Ru5~eK8)I8abB^9x?+qdQR0^oRHCf1u&&k%x?NY$t@t{ApU5wC+s<(b<BEVwSOyuff>zE!Vuu)1>r`smp7rVHd+CFlFeNJ849j#)Y{7p*7snM|}kFP0{w5viy>weU<$oXX0&d2SOXR=Oh(`dRp*U}dzaMP@z84Eqz1T_xf;43MH{G)oIW_D0}R*O~ZL2PPT2A+J*N@1oSsWQJGiPJ;m&zC;Z6wkC(Ek7iAQQF*0e*$@xDbNMJxD@pT+X*8Lv#0pTabJ)R)qj{!H1phf~Z^`^g#>sFqpn_OcJ1cJOZ5anyKkK&uqd4<*TYdv3E!F<(Dk3_c8>R(Y#f&Ba=7pyQ%H1;HIWx*$h_;NXFPiIX^nbIRqcn1{k#IPKTfPk7HubGu!E(Ni*CT_4Cj)UEOzxH)B7hw|?e(?M>2(fF2Dgbhi+FLgEZ2FXzXW_b)W*<Ss+F=-S8ObJ3Ua~Nd~7uXs@em|p_)mcBuN&)`=%rgk|Twc$E=#d@nUQ1mxrPz5mwa52Kc0Yo(yQ-v}o{78>Lsq_FXosf`d1&CBvdtUfA-^&(762B?nNxyBI1L60ju>hoMpeyiWnhVaS7=D?S{ljCzqw#%RtP@t!*p|0rnkdM#;X+1XKcu#m!TBm&tb$%Hq{+Pj`UpKw#(K4*ZW5c&h|Fo}qAih2`K0}+^&WNwX4P~(sV<^eOR0c}ajC7>(5Fo|3eDZvs7^LTU(TxvxmW8h%4&4t39_x>xT%->=Q#S`=74gp{UH0v0hf>JU`-jyF=yC=Jlh!e(_u+lol$0Cx4)dPN(?9#Sglz_sS0B)=IJ9Uc%U7<>4(Lw{Qr-+AAMI)OLMBza2Vr4Ovzj1Wx$SM&JLarHy{@QV=C`D4afL;A-dV|ofx~&`<)&s;T5q!-_8q%Sq;Cw6wQTcgpp`2U5LV|t-{b(DmIbk#Hx)(hGm*bbi_S^>e%=rNrfW)|o-J87p(D7bE$uJIYMn+Lg)<cl>lB30tutyn(%t;CPX-@6J%uZs6?xTQ}k&$4DP^yeT8e^6)B?1HUlckF9o-=ePin%a`{PZh9_T9)Q(1}~z-{_=H4eV$+b4a0OS&OcOAVlYjIk(~@E;9TUsvamMEoSBn`D0-rUo|NRyVkjBq#??PVx`E_WW7fgVP#%A^R-+i*y1_kifMshLHDP}Fj98|)b<PfUZ=1SbC!_Spn|w6KAn*8EmT#au#5Pe=)_glo`xaOw&#7#>bmwf4QnBFGDQO4Sz4H$*j|fNsI(+hDz9J=3?f3z2C03nue{4szQN3fTFK@qb?SR@s4qroDBWjBPu7x>t0+LiwLZCe$3G<l<+A;h!B(X#he!zxKy8h*eK5brO&mF-Syh4*4}om;d7ov2hM9lI`DR*-o{$bSIh2^&5;_QOLVzW=7`_w<^o0d|RM86BY>#?g{w+d0j69r#W+YsZjPziqhqS0IYU=u8-nubP%A7i@%46(x(MO<(Wz<Ee|EzHmx$r3SX(V!Ph8K<C1Ue=m8=<ktm$H|{i=>)y)LxhXm9y8h5Fm+O(R%H2pD>4>g&XU<DFg^i{+sXeYmwZz_$*!&weIzZm2WqyUWqGrl2P1jYz<&f`OPXl<5s~EngS4IX7tQcP(BQ3s!EAut&zFF_g%$xUze`?{N-GCo_v6IYDc&Hv^0_WS`}1isz(aEsxndtb5Nsja;s~dOan+qQI#2LmW|jZN6aHAFn26HK1%g5z2rv-)EMsgEGj{)=^Ija>%gWS<utz84fg(<rg){onb&<)a#-kM?Gi1XB^GJ4fsSG+B(fXLQkyu2NR&?ux#)UR_56&t1_mA80tzjcby%(EqNajWogTBM172X*qmwG?#JO?Af;I}Xc0tuxv{;GqCyS0#&uasBGI_Bb{976^ePho1jRD0S2;02scqeVNp`kjQ44!i1rg<nHZ$i{1N1yIM_XYM!Kdt#o1}q&n=%VpTv?~I)sZ;j#8A6#-iL%&iS9!wZLp0dJWoeXd5vao;@RX-w!}~0g9N)+yE?3UDc;8O#!WjR7wXV^6!%BWg*X50oBiTy%9?m;90^+Dpp8zkd)+YtfFu_iA@j_GP#-UNhCzRy-WXi6K?(*%kL4~G)HtG<D)~zo=_9j)q9=1YDDVO-)go$x2Z*)&W(6bG-e#gVVc+T*#y|`@EFBC68O|VfTYO@s&n`5QWCYC#i0|)#_Emt*ACJ^-x1<y|rij4k<&wO&^bZ)su<PHuW$_vQrP0mx!x0bmP=m9tIg;7tIQh_R4X_1&Vp;}>|ev}8kxHToLiV^u~U^UwvEzZx_umo};XMZ<|*+sjSgj@(o$)@2+E%}AG&gVNE>eL+mWdU)@hA#@<P`SU(9qRx-4F&sZ2-E^J@$R+8;&ZI|K2iC+lh7v~ANkRG!2CQxdc8V96D!n@&xft(jQc3_TPjF(Qf6$7<pcLW480i1%vwxd4|$^-n_jbt06dFqXH!#@qVrNDUe#ShHFD*skU}&DFBmTz$<#QHnw+UI$ixJiVNXH*SozP&0%G+YiBlES%y86^6c~U?I}-ON6X2K3SUV<?5Wv+iFlcd57IY&ORm&Gw^vozMoDBtQQF2W-p_^0zV`NLJ`x-$$Tx6gfd=kphIk-FZn0k-VA&R3EZc~Kys*;R}Nu-1;H9bAZ^S-<rxOzF)4$zuklwbg;vogbgTthtw1vCn$YiKu8BQm}rytDK#c}On7;FR6P=<kAijWPfBB<%hgc9E3|4q`csuSV(S)!IIH&k4^pG@fhjNYpX7B&YVPf&`{~VH#)``Sg-67A?GK?*1F2qR}!#d>=Picc*w(sXd9i?vkQaDFQtWV5&8NT4Ll5-GxM&xYwvj!KIt*rHqT^DA0eP4DddIPl6<<dI1%33&TOWgg%XfoSk_hS40h7p~o=-&q0zzKh<swZVXM;s32yPUr=tv!GDgY@uq3cg21m-RwX);wOO-^BdTF}Nm~%<W-H#UHC0knTjPId*&NkXNcUEc10)~P=FS9zJ2CNKS43stH(!TdA8@vvs*m$$rz*i#>Fh>5R>&~M6S``hCW$gax>o~+;-+6)V=m>|SY2pguQlu=qBsDA4oXFb@*BXgsNVu&-_D1PEmjq9?7CjZ^mV1_EMAXLKdDe7im(a5UzeO53&AmBytKGuGBHOMT$t(qy<Kzu5(@uYwOT=Eu>~tzCy|{mi_g)1H5LSjq#CHd6{5I7mD7%e0??-##Fg5~Qbpq7iF}tTD8Rf7JhH|lh_|hkW+M_$#2TAj+51Xu0-U%NSjX{13_n}GU8;fsucjbn5Yfu$Dy(&5q}hlIVkB-?v`p9$_A*kdq}v%>sK>|*BABX{!4-oAv*wx$d}rgV7IpsWT&#0pBPwtxRIN015gPin%1<LjJ!pCmO-X^aWiDw$0e?!@Tq_C7Q18wf{Vh&;dGgaNnTGlZ-8<-zX=qo9e2WXuRNN67WfaPKMzDTMg^+BYy4Epy4O@v-#;^;FjHb7Mg?C|a`cQJ_mru%0YiE|&d{t@83uXqLu9(+RPXpORoI9=3v6kJzu!z?tBL&d?lo5*x2B0L68y>LXILq80nH^*5JqAuhUeqR8Dy14=jt}fRV_{}WX3BGgjC5m(qKSMXME{w!zyLNulZ4e94?wpuyJ2D6F{>&?pxm!yVYA}&qNt^YN;3A=qJ`GM4%kG+SI$q<@TYh;)+cX~BM(TdN|g@6O)j~U*KO;N^1xK9(8=%<dqEZ)t+t|WC;AK-H`6(~=&%Zz_L|4&Ycnb5wv;DVJHcys5FK`7xhU>{loq*F_?l`Z6rT_+oU=TGi>TSqa=WyOZDP9uuZHH1Xz7h{F{L&<(MtYH=1Y=^VfS1Y_HvMKys_y-=bMTKgkIrjOAAj}r~R;8ay+q>7O=-8ev&OslRKtB9h-V(8--zoD$sP$N6J$#wc1l!1)Z?l>7}>q1e7h`)R3|TD{=F^*R$!YrGt$=y~s^y@O7Y#MUX)VKN&uuq3FyIG0LpyQUkWR1aGXh?v=O=+iAFJI!&s7ZYHqC$6kY(1sC!fxt*?2w6wUGUB1>)A8)Sgg0!3ob*ARZX*86alnkJYad0Te^oZK3Xv#3Gh=H876eo?as$rbt+gD!!l24-UQ0hYK9?o?JOn1@)Y4ZX-SikiI9HKd~uoX0yj&XKW7wt_BB4Qe|(vrd3QiZxF#KLAzjH2!w0^<2){%%&to?>otm=r}(OLUASGNgcYuO5JuTv0h(tNU7YuGSXh6)B{P`oWA>lT0a^3bDqCYeAAK`c%6Q3|Xp6qeuk%VzY1{#O#7>D`!gUVTq(D^3=_rG*$-&!^0aYLKnoK+mJx2rI6lQte{z1N6jUrDVh*1DS&UpzKHT`j2T&_?Uv-$D%6!QDr_Wb1Un6<->y2g_<>DHMaHP&D}=39=hFlmVN4_`M8t*qRTES4DrF@wqgqBwRWXz#->m=TltgPNq^*c2!NuZdvMTVIo=vKypD|6{(l^-zV#BgXOd<+7H*y!@y`#dKfl9Bu?h*-UEGwwCZ-ENahL>grqXU79jB?Lfm%3q@kBaR&lPL>&so|78d}E}q)n*Ym!g2*}7BLUC*4Bo}yQog?t&v)}^_0t^g3v^;tIuqbL`$y2#^@#be2WLmZZ?<0{(Sr9w#)olMfT(ppI{?9a!6gA*&Cyr8lP@8Av*#$S`@e(8Zm<=m~I;0knD73mGU}G8WAfWW=mqFsqvyyC`my?NK*RCYFFK)icblpMB>Wxc?K)&N3#%_Nxzb69&}M@ym2<0S1MZhP+jR4S&n2cR>3<@CvE1{k?V^4EuAWgie%Zb5P-Td?ajCL6!^7qr?C-5AuvJy?JYsJo8Nz&+H3uZV<U};m^xNX!@M|iEYw<efV9h!$TGFvUN=+h48r#>!5Rx|oTD3virmSxFo`BXd10!IaKQVvWn*%Ax%$ed1Qn{w)F;ij1C=a;R3(XTCZ%knjHpnQ*7EpPo#<rrt8hqNBGbATiL8Q!U~*x=LUfojt2Q24z<UWbs-%MRet?6q$y`|(zmT6VtA5?iC5t59sR)%$y)lwNv#M_#Z`lecnpK#jb6%*Xg+^&-)k-o-#WppSJuJGCl4Iat=|sD3%4~8dLhOKPs~RE-ASvvpvf3Z1UBJ={g=!sVCA0x_hwBhhOSt^`VW5CnS5}yBW3g$RC(6FmB=G18t%~}6Jr189TSfQvnN~U;Tyo_ir&@uDBE`ur?uSz5>;X+PaNw5tt|fPEm_J&fE!HzMnS5IozFc=@#w}~W+FD`E&3`cCBxW3^o1M8jW<YLoIdNwyiFr0!-1%x`z7#92Z;4DzpIz~VIjJdx5cOK{wtC84$}^TgG>65=#DI+?rI@@U7LF^Htz0dF6D0WPoQu?>6YVM)3Ob!|WDgcr!6LBlN~TZozo}+J%*<m|HAQBgN+2<J<(_@GZt+zKZ?rn~I)m3Kk)dHJ<$QPK=_x6R)C;vgd8kBFiAVw{1>8&9zA-AZG#C1u3rG_o<Ati2Xx1vpj*cE?)23CK(R41stkMkf>gn7D6fRO~`w=6y9xVtSF;RpMeLhdtG+e1=PXqRns3TToF%W=XR1aTuX6w<EZ?Q@$!v!<-(^b0OB16|xYnV`ZTI#|@fv@a>&XF&<{Cx?V)z|j`6tu<FS~!>)PG3L=BUq?fsY|5yty8u#AE^_h7@C)SrD_<zLBEUBSsS{o7gP~9s#3oq<`}jVy0|$9%WxvrURrmr7W)+U)VwXNInPLx$SI0YXmLVZSjJ8VNm@%j+&+6b#;nF^R?03A$ufC+N^MlJ9)XgBWgvGMMkT3z8m*R)Ai!0@8Y`U2maC-3EsY*QZ%Uunl+kBJWN6UYa8{AHymnJ+WKC<~G2bF&;xepHOjpoz3K^AB5MnyRvZL~nRQ_Dmj0o46Spqb|T{En`c;uv7o}9tO<=LyAZ)goJ(-~+W5Gs-$)Jij90H7{6Go1jmk%xWJRZRKhM3pC8^>$0i4Q;*<*B39ceqq8|LtvbVaH-IgC{A`l{ErQ~)IxT@D$4D}lal&#J><GH;X<|OP!%~5y_RJd>kIVRSs{lo*+pWtQGqXCQr~DlV<K*pQnm+JE~Yf5DbNe=#E6AvH8A~F4BA@6Gl`I<jzi}Pn|E#{wjV_|r>o2rY}=X`?M{R6f-E%ws$texYYok9qJXAaq%Ofh8^=!0MMD$w`x=GYYi&|FWdUWS)p0DTVhmVeNsVgR1?)vciZK=~%v%TGgi&?jRn&hdlZ!Odn<!$S+2C*RtdtX+)sV)L1Z~==UQtsGu(U2tTbo|RQ)%LQ#pT7qq&ad(i-}fzm5$0C`EyGau)G`t)h9*%{al)Qp5Pj>;+3+onZ&uZGkdq0rCZI2Qqywut>?24^P%H%nKEtfN}Veq)5;d4vCi63vSBw7XbG271Wu*$M<|PO;0cLpYrFrkZl7957@n0GAgN{2HqI*!t(vwh#g59os?|{;>>#yR$!>x>&^{W$L3UiR!2lo<f;Dz7q>5cEyIi_8>HK*TSB#4o491bAjM^n%hhuYdhO<DCN%LShmTqd7a9?;k-^wqYr^Z4F#j(HfK)hjSzd4I`BU1<URg3Ik&8o*P?}b}d>za-%j>9UeE!FQOleRQF^p-aywy<Q>Va^5oGN?o`j~}Zj;wAVH<%ckP6%g!L$rwEt&OT%X>|~Bzg8q^uwWZj6ZEU|Bzd|RtMOyP}iH8`B21+qtj(Jp7mlLm-I$)USyych)YaS)1Kx5yj5y?ec83RsrLhz^@5YXgo!c50IgTxaiw}p9dN+J&H$BjznA%~bj#8I_=BWtl^tpK&OgBCHcsRgUH$^Z-zrDA`=KnMk3JKE>!NskzCo4Pun1drEp1~u22XV*}|AoMcAhAvH7J%gu}JWdq^mChSS<th>sG+otFvu=P}=w*Y`iylssR>?xSuUhr2mQM0nvqYVplj+SYWepoSYgGqXiR7~U>Og6QvtTJ7Q0-cWn99l$_~&y&Ii^(oqrR^@rzGmDTbwEmJdu%Mo4Or!w_(L{oddZ#zNBj^n{>X_rG9sY@L?8mD+KD+0BWo5O>q4zmfs-=H`;{Dv!`@!H%_XMPAG&8Qjn@p_Kl|Kgt!WHVMVWrA()mpk)?M>WP9DBwM^FEtf<*m-a^roQUskDc7<i^0!$~xzG)TeE7f=sl@H5IRX3>1lfNkKCJfii4Fp2Zb94a6Kxy2ZtghA5%BjN)8qs1BImt$)!g&g0rKTQD*BQ2aLQzm@d_IDTUms<A1Sp;-fFAFog;Um5%Z-w`gJPuG+zwjR9Gb-@9b6vdbz|64Frl9yjKQFmLY`Jb2_GM5M-a@AYVS>J)L2c_$}s4ne$F0cW=EyD1xc`SodyzVR3|6Ut5?wTTDi!ClTIsOpt(}PB?8FxI7?JmiIO`R>{vfY6U`S0Szt{NzGYFj5}qmbli%7EWcfrI86Jd*SRz%fVJ^w7p9C9|5Q)o#sdZ$w+1uACm0A-1wmHQoZ<(DHW2)C3HR`l4de==TC*hT3sMgHTMO*G_&At{37UZyx5@|Z&uNx)rB*F;f%8^S$f>kFe9eYDco^+{_K<ll5_As<QYzMPuX?;OapoUXhw8gJ!HiS4|gjECqWuwa8wq6K2t~o3gp3^hmz<Oeb$Ci*L<6$Y+6Lo~CNLb0d;Kcr9g1Rnq9?3~%DkQ7KZ&5-E3YJ(6ioIvOkSN`9o}3)7N@Ici%xdQ(Nyk9tF1K5`S8(Dq)<>=s5G%xDq-E7w3g%lgfrFID`lhj($1b3)u~)>xuYJZZP-2q`7uS(;zm1rKgbBllU@<8X2kozkY1TN&CwI7b(TFfq(hPuQIQg5^G|p|QSJO*;XrI!)?Fkwt2QsI#D@rPrY6S;B`UY?(t}7mGTdq>TvE=umQ`gTb1FBuYO5(X!gfqOqs$~L|mj`1_si1+xee`N}$prDDh_@PR_E1YEl3wHl_0R;3%@k3WQ`dM1haMjEVtQ#%&s2XmxbiBLRi%!qK)xck7Q1yj_ZAO1d2QxMA&=uDYjk$&+>JmivSQwNpoH=!^2&@$%Wyv)@M`KQ5xXR{beeh!!bgE7s$WkP^pqZcO5LE#_Ejg<wfD8&N-re+^!Rbyj{P@-54`u_XS=T$L-$rF+oP)|mHV*l#PP%N$CGc;hH|z2Rh#|qe9-6r2jvQcZ2')).decode('utf-8'))
_ACTIONS_6C8S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<+io0La{L!Q^Fe*%#cv#`*AkX96ewvM>j5zsz-t&V)(>O98UA-`#lBS4iHwZQJk_KOJ*m-bRh|3EjEs!@^?xq@?e{<a{<l9a{^{3?pT2y!fA`zRyHB6LJZ>+ZE-(K5_y7FY|N8ouuOI*Z`yc=DxBve7`PYm0AHMxn`|#73zy5aj%ZH!u?k_Gc-ahOuE|<;MpWbh`9|wQ<wB5e@`t|Pp_U`k=<@Mz2pSSl9zg%1{jz9nS`0(z_+s~)}arN}{zn8;~ef;qD&tE>C-n1C>?bnOl_S5HYZT;op@$>s{pN?NmK8y$A)As)U^w!n%t%t`AUIiL5eC_GebSh8-Ca*JR5BBibl5cae81;4kEAp<7_jhl%)_9`+9R34%+oav(t^5Bn9M7g5-@g0hv=~Nx-OrTqGk1iychmQumdD-a?c;P2O}`tj9=LRu(?#^@;mdRpwTtsl|JWI$ZzjECQ`rvAcz`FPbn4&RyZzEU{OEaS4!Rzi%hPbRFFlOH@K^41f&GUj2keAq1(Ubz#~zH?U^to?Yk#B9*nZsU(2bru-Fc@WY^TXsmkZ%=1DnA-TKU;B>Vh`1=+N;e@6b|xEah+fc?3haKViTedGn?Z;_)5F4`0vTPv}Ez;7;RSdGP+1bkh4ipH6s}4jlgP;7whh>wb8F$4+jQm0?XfhiTvf>GRa-*&5ltXK%sO9w9$%%!ocMc>8dFzkU1pw?AzkKYzIY@Gs*tq0``{UlLd%>37UD2ZvjG&>nLS9UYO$kBzH*^AxZEU-kMA%<r_1>%4dC+J8lx1ekY?`8Y7b!NSe>8Ne8Udjj`rzqCVUGVjB%w_YFJ0R)bHz#wI=3jE|fkc|cU<UWvj1fu;|@JH<?CmkqzP$k<}*+A4c_vfE@IyKi<0iN8)L2o(WJOJbV^vKp2^f!MCoDkd6Z(rzfuBl3JvojmkKc3eAY4W`fY^XH`uooqx00GIOslhI`+7-vp9OHI&t%Jlh=otb<s7|^Vx)=xuXEZO3<lV@?_0w@(8x`=f$fK#T0N!HFzk4HSHblxiA;ZJ1HviESpayVS2mmBF7afr<2Q*xzT~GcgmiGS#Is5V0ACC=UQnvLHj@5%;x)GIkEUiuE%*^=WL2xAL@&&+<TJ+GfyD|n!3{r};pM=D#UMRcMjj?%u_xKm9V^zRt&>h{?7eml!sE&O}4$*KdD*S+UaM}RkkqJ;jLHM8_JNEq6pfdyPk>j8YN6N=C05~#QcBeIZ7?e}EQXcfv6VatIeBac*3Ppzx1Pgj|fj4Br!|j7xj?)hV;m2dE2+zi|k@mm4`L^9#vuUG)KBf`1H<dnpe!ScLw0(U1D_{poaU*t#!44U3Up!Ty5I@E=Zb_Hm(oR2;<3^MoKXb<|U>Hu}t2(3<h+?py({3)KX=rZ@A*vW=#DiI-^>O@gyrlidX)x^JjvZ`6%th@Oc`W%G(-BCn0;}Jlub-QlweirW=Z0n?p6$Iw_-6ujI`X&-&Nmx7?nj*IrJ`0>5!`2UMoYy;589o!f7REG`1pX*C4xY^;vZA@+rw8f_X-0b2Djku;o<&UnhG?c_J7>Z(ANX<oe&8;`Qo8)U79|02`9BVJQ+Em6I*0DsMZA_8?lGUk%v47odH7!Wc~EM<$K4#Na9Q8vXxMwQUFzVJZem%Hty>JR}z@od`iQQ+eBCqG!dYfr%xHM4uO6H{t>Vk%UdBZ0_~im6K#4nWcC6ZYxF5NGT{7ak=<$RIme>{uEoSkoy!=y%H*JigJuwMfnl??Z(P9~(Xhoe52eVnnNG{4q3j%c6FUr0hG#S~mg7~nGXp|Et~qIZ?U`#FCQwfh;GO$vznAHZXgOV%<RW_Xlu6EO%u+;oz;wOyv|brg5a8EiGzzw-H6~QpF?5%o;&>tURM0wY-`gG=;#|~1?ICj;w~pQOy0K_pw?;z(w=&p-?GZrkebA!G-;x=w%qDO@q#Q)hU$axm4wE^~bTe+$k?9^DddO6#96JNO^=vn0V;*1Q0+unlUpoZHvvr!XaM>va3A%X_N07taxp#y0E<ZMz&H>DdxnEfc9%o-ErbXI*N1c3ki@k`D)Xb2_*WNhrXCaRwkqkkNo#P)Xl)D@&?zm}(IId;bAAT!@Q9U6c(P*T6P;4I@-ij$hspxnNIs`}K={VkB%s+p)|MPz3S?*B#OFw6>f_m?_^z-``OMj;>85R(pO0c-XumE>r^cf_STd?B5))wSoLVjg1P$VR4&MDvoj^+~`b7){SFh|SUjJaUBu{_S?@W}9)o|jJAt`Hz>#&YE&qAlNIAp3=lR^(%~t;7dr4Jrro4x9|OyMSm}`+#I*wB@S;mqkQIY(K{5zQ%Cm)~aR>T*TkYAsArHz&s{CWb?JDCwY$6u>;WNcPGIJr9p5Y&_)1vnRlklKC$gdY&1z4&|r6RTOu%PA@m`Ok-Yox&$1#Kpg$1+BLf+Et1;%@GMpy<KdKD>0H9M&@+?OQ4K{T#LKt_{*Vf%ney7Pn&EdfVYsGWm3Hde_)YScXKTOvcKbl)#aqt^g0cQPRlT>zf<sViv8JVNsu3_%y^y^DH19Z$PTjON~tSsOlZT*<IWA+ERYioj1xX%6XRvnK(nq<f$cS_8Sb~a#dwp2_k#7*66>4?bWw}Rt}y~}|=1#i3$r-1UGnDiEhKT47;lJnhq)4*mW+p-hPA*D;*3EnOEo2VzE)3+^fnxz*>o-i=_Ko{*_6;qg%wa^-<O6amRUGoG$zR~Ayad-)cEQYF^;45he0ZYg=t;HDKc4c(&&d@Ai%5{0=IY;Ykt$L+{)twg5N7AM@b0F6$IrUEl71FM?PuO|6z&&BoWCHhj-831NNCohzi5HZ|F;>>~Q%$2->5e?;vrtFD%BTrPX5GmQ5ft!VB@Q`^m7-^qRR$oD!||(aQoiZIB*Qr5Rcb1pm*tsE_G&$9FhIkXh;iR)o|yV*))W|^R|=L5f#KUIH3iBhX)ZAhER&UJVD>tl9lY3^XWB&YpWXJhB%ox-3^xOciJ3B5ers>qkjUmqzXcfEnXlXS8!&09_FtK>=wcBtE!Zk%j0rF=JWEjSRsf+32HYF{mQnG=;QAW<-)!e7qg-qx91h`@Z)3TBKTxNql)-jAZv6Ggkm1QdTsf1wV}}SJO3S^z5)Kg!PX@P1a2E06s4Uk-(O&{S9crU%Em@T;`HDTg!`D6qX<=+WcA5cY_CRu|E+tHo<PG3`({c#Ok;1BDnx?S7*lPWXA%{tT6*aN|pV-I7fbmUh20zQBbV}Y{rV}hUc=KA4Ev)LoA@6*4(#9!Iphvu1$i<e(909=+;C%`}4nrQ~wDI9cWrU1mPDVL}B=+2q4oDL+)=Nn%%Pt&f2MfvVMk12ka!q)%LVGtR)hFE4H%}QL$%X!aJ4`~joULBsY9KDNlGm;A2`n<1V;(T08nBn7v;w-~8<Qxwcywf;F_uS{!nxK*G9V7dKDcbSE8l<Jw2578*~C;nxqIM|)a!Cbr+}5rrH`tVu$`4%R>VQ$3tDL%qiYdmMDy^!Om=B!*Djz?CxGJYey46Yrz=#@%v)%n^%M<Jifv>QhbUACUaTyp_BRnZJF-f|W06bCp}%%qDoQO?u5)L9P45%>RkxKxLw<l$B?7ZK<wH8O6u9>_BaEMSxuv@6Tu88xATu3?a!$BST^^$+7<2q`*q$2)yO|%H0Vqv0|9hKPDLURuC}SqVsgV(uAS1#_jmc4FNJylOQRWnf;<-?D{pLvKi0-j~m61_u@er(xjv8Z~Fu{TV9w;js-#%riQWTG2^!e#mf;xO4*+3_Caet$eh&8aI<<ugDvK3l%Eg&H}U(D4NCvlnKzEF`tDYG#%XUHFO>;0-ZL)f*>O(P9odh{zr#U|@Lvgj-G(wVOnWr;1HGOm~wBo^d>dJH3VH$VwM$M22QA7aju>(5Eptm5GbIpRVoCJMrc--#}ru@W^ziMBoOd77&{zJ*u|BVN8n{F|k{>1pn@WQAf)La}oLpJ4D2Vnj&otNYQ<Y0uY&XT3(0tMA3xJ{uLHb*&+-S<7cO5rTx<eR2bje@X_}W!ox)yGq#+o|qbd;fi#BFu%u5>^ZAhNrM!Bp$N{js|1ZI|4yQ%J)boTlc;(V;IwOkDn2R3^&X;`1R=>r_oYbW&n*h1N?y=r$2jZl-#j=Zkie7BorG(Yu_eNJB^AX+O`)HElBPN_r;$|^qxyAGR-hSa)MK!JR-8mGUdmh?iPf7SR3of`j)_ZEC>9D+_L6wDn5jzj;sys}efWGK(q*yl6}{Ll_X+dwSuD~fTp@g5^55bJfEMQU3)tdCVRf%ZAbq!0bxxu(DH+wyVru}=D&DNtHLePs(A)tprK4wpgYsd(Z&k`HYmLl#^S6fYzG;2;#mo8bJZk~%)Q*1nX=x(uHWO7S)iecuRvSiy$*W$hx$0Xd^9Rx)R%M3DdK0_kh{f0o%pFUQk5a)*FB{?_HFEIzCZ~l+ovQ=QdX)P3=6PuM-*_g*pfYpOkM&j`Vtw0(g)aCm@#$GclEx|MsIo%BzTUjmR5e6SePYN(*PANvXS_8q=<pU$IJ>OFYE2k5hs1Pxf^{MA0>d7iRF%h1sv{P3ptx%nRE>p_6$(JIa5?q7ws0qt7l)&Nt3bd%Fz5ZofZ`5>if%gINgHiws17HCXXiw7KopNRp$3!VR`-Zu4$?!qtJR+~Vi|FR&Kj^pyTWmsI;CyT5X+RxocU(EN+Kp7yulVO%Ru=TfmaLyPkEj;yw5UO^+k$tyK=?_0H0+t0^>ih)-}$rTMZBi!n_HjQ&#!l!+FO>fFBjgc$AV)0v06;pkel%=;FDi%yoog>7P)N?~^IrE@JdIPXV4Z4YW~*(6w&k+GWD_a9k~|EQ44vUY5dpQ&Sp@S%O+G{YEbv#@N+UhO8Zn%bI?ncmZlkj~a`ct$5g+P=0M<*^oG}Ly*)GSsf7rQ8-cX{1k;r?~nM*Cr3`_mTN3;=kTGtfV@!UBISH*X&sJ`aDgz4da{yAT!keXiD~1?9QNr)dj*JFQ^Kkkub&21v)$3+{EQAuAQy7>chja_)`ceIB1%fC4bOPVFT_ng{o%Rn<>_A*5T|tb!vidi#H<}F)p=arU}eGmH$w?P(8Sx<8jH`-=KDnD^G-sac)aIF>jCq5g7kV>gAyw=9-ntx(HZwq=C>7_>Llq{jO7FO-wnM4GM%+3y&m#LH#WUy69IS@+0N#sD23~#NW3c8h-#6^Q6YtB3|=r^IFhL`kMLYjoRBFElwnUnHd*=4$^v4QA&FDv6x)bMCn+!h)r2JOPbR=GnX%!RNJ2SRL&c!QL0Qm6Dyo)Du85scSU4LB)}rK^rb0Iz1IEaf<oY#&yt~LiJNP7Q1=&zLy53`)h)ih|c=Ht-6Vpg3S6#H+=Hy;m{@(iKoI5~leo=}6AkWGi19B1dpcK$JoG!mzBu8YtLwIZHU-F<_g2O30jNab`2OFdQ^*rqU5_g`R3Jzd7kgrDW>}>1Xr-bk7n$MO);&luz$*BdaV1X%bn1<R#M!n>Xc?&N9x=$mrZHQ3uyvI$}9V(tzTAjpc-<By!dLF`5%L!HD<`KdRi8XP*QB#UbH#wFxE>^NY|ABJA`-DCTmY^yI81xo~gmejh1`cv|=860fHGG90mn%Pb(gqp#`#Qjvp~)HsW=0tX?N%K8XTO8jr8#p#zfwgO??|rBno(C#4a`f@gGg3e@oGa;CB?Nh28fo=VXi{Dw|X2P`Jgs;CK%v}sRz#$R|bCbmFx9+oo$}xkzrWTf}PUYt$M7GVf6dBu1=Fg8X?`YC>eg!uR>!kW!r?hP~oo?_7Tw>08$67rbGJ;;8@tVfY`VBu(9RZE_F)w>nlpsS-u_}e^S6k6lN2Ezb;uhAp|E7<)w8Ylc_nf<ie%?-|Ld}=O_TMQ;QjNmRktr>m>5?W%)VUuVTFbPppCZTP}+06iDq@M*w}YAg<I-mQ*8$C-QBo-T?D5@W=)xLA-54i8dnjL@dwQmA|i)F2Jc<j&<x$#PD;-w@Vc`;KdfC93om&U4^x-1Bo``f*8r$H7yf%M0gpg1=hnkT&Ty$3?i6nB8SVu<BKI3_|C?8E$aN)Y^=Gk5fwNTidqJh5eofU=ckdP9yCFSCZ#~zGMBcYfIqEkuGNoasCQ?X{)$uHp8PaVrcffGdj}(A8rqd6<KoOS<#&We8HK8!9;{y}8ItW&*TN>RVJorX7_`VG?<<0ZpB3WhLo;W7`wC}TJF~<V7DD!dxk0BZ=5>_RKsFI)PpfpSRd+DV<F(010dzlQ#KOP;loaxS2OMymW$sUk9kUE9tB~|*o}%V;*bFfH=htmuVP-07%5#N`^uQ8D6ZuAn{xfTV0c?UQ2`fkLfNoLm0&UKQ3lUk^taiO9YpJ1<M3QxBN*Ub<6Uz?RL_t{2Pt))xe~#_>T;|9F601_BgK(2e?&MW%9a0{cY86Iu{KQ_61xM?xsN0D?L&nW?jxIW^T&BI|F~-%Ilyh6kl(SB73lE~h9#}4lmnS7g?i9YJS_>ua?+E8C&*36^HnbWqEpnUKuE49Ixg%PFqhC&`h9`#7|B@M#WMbGo*M+_8WE^k9bfWpDqJYpV9Bpag3G1{UmP?K&w$dE-n8Z&Ci__$eDNxDAu5F_*tWXV_4hl(m>ZMkFN~@vcc00ZFR-J&d)f)>bTe2cI-+M)y&T2Z?=+n#GxCUPb+L#9!xbRcJCk$vhGenFsE4q|{Emz_7)z)KGZryeUTs560)ju~ASmR@_A(#c{@*26Fu2HnKxLCM=ZA5>(T-ybyITPxP<;rO^l$@9hpo?*E$jS8Z+N!9^Fsz7yoK}jHMp%twoSVQ!CHW-k4y7)%?%`Zz!1PFZAZ?zb2pexb0f%T#ENlhMrDL2O)kS-ggNT^Qth8kCwp5|+Ru;SFiBZ&@LqI&gED^C-JtfG_TuZ{*4ivRS$5<jm3Rw5*0Z7Re#^Gx2Yt^~hgdi_ZBVAMwX1tnYO3_q`)lXb=l2p+r>plnwQ=J<{BG?z3g##hxImot-OsO4~NXjBl-TX;obzsmvyrCv^Lkzlc38cjoQXR~Zl+>c6G({7lk^=Zf?29PC#+Z>NZMP-2now85s0brbBiM;6JUeyAmOrp5smvJFe1)*pdOl6C5ynK4LPT7sUp+A;uToY53)IV~)D=TX@@4(6NKv#xDQ!hO2`-j+CaVIU>Di=O`WaKzZGDriBR4FI#3Z7Si$LxoymwSs)6wab*IgnZjb#N{`xdA$ZFzBKFgg&pP+S#R*oNgfDwgV{Oi<8E3(qA@MAFx+Sp<%-T!WiM%nO0?r8&7bfket(OsC8%08Qk%GPAi6W|JgZave5CFVW{abFhSF6L3y%0xMcB=?OM+MEt1ex_;}|N|<h<q|T>XP004ZjoFyR0ce8hrr|Bh&TCdHFV)TKh+O$FTM{cxjhCT9Npd1WHKjjCyXrbseo81N;@6(fGg#pymW9ZI^ed_AK^K+A>&Rw{6^m9rm@EA(%aQCw6TFM*q+P};$#up3R*^c2ie%X#4_Drp;ofax3jEr*)7Xfj5SSqU_D1oR>(`3Soj=18Pu@sl!l#azX_#kcj=5Uv5g_fnB(h9(x7W=Sn?d;gC0Ju_m2-3hQIR{D7ADaoC@)Nv5q5arVQ3+jm#eRQN>HJ?OnuUfJ5b3o*j1AF7NnGIl@S%n(uO>~btgI*{mLEED3NK?i$rFiBbZ$1un;3??z+Y!b9gVVMwL`@J|5s;Y_h1VOuUp|Tvq+6&L#6C-l+(cPQ3{vfo4_TINq`oP_$5ClFoUdnid+Rotc$nl!|t#RCWuf;dNNRF5_V7M7wUvY>H5Xgra)$3Lq)$r=yck8p|RG(w$bBWR=hc&>gNrNG;*^=ZAp;W?frjzQ$tHI8T&)sY&3`6>5t5eLW5zAF87J`b;YwcP_bhkyEX}M495wT?E=?;9za@T3e3VFi+H=C)$~qDVa70rrh{Jy&9UfQ8;mn?}_^cdbujKzs`x{M6;ReVmh>@C>w63VwkfL;^wQ4`BHqizQr*$Wp>32=5!_(Jk;yJhjmkKQ$Dc-pGEkKOa?fRp5zmG#FBB%vX$#ZaB2h}oj#FR(Q$@r(#TEFiG(9du(1=Csj@vj_l{M`6uEaQA*7;F1nPZSC4!cz0)Z|IFTm7|l)~u4?FnpSCDD-jmf=rztYL4XX4sV+grlj2d};&rR?6i&7Xp4nNO!K*C7LxOg|XUInOdpxo#|YHS*3a5=E+-w|CT8YeUJHS#{is1OmyCpY(jTMwmovVN1_Ut$w46Sd{z5<nd92ggl)0LDMR)8b?{0i;Vm;HJhd_j6`iH-S+$gFjylQ3>s!#vUf%;qFD#7~TD55`*JtWEBrk$+s`a;K84=ew<SS1@;sYePeD^l_30Hcpirt7MD8N(7L8uW9IeVGXTVTb#T3qw&6-nbdBs&31!&80z0%CJIpiwQ%aPt()1ZI^;vx0MulvR*jr&KT%s|F~UQUR1L!+RtZO1;(MhVi*}SFsMMY@te;+0y6{?4|W#gJSor)C&y_2b@nN0k7SZ8l^I{@R$$b@?{x<Cngo>xqyuDD99zvu<WP^Bo!%Fl^xu57A(~1p{W^eoj-C?#ZAt$;v(v%hwEB{t8|_i2wIBN1hpQFTGB?yutghr*cV-EluwRVA0n!;9@1Mwo6kk%#fz+8NY82rj0q9O6PgmmX--J=u|bzw$nIA~U%h!!QYEg3sFo%#sFnsYk&qA^ht$$94bDlR+=82uB5}{C3|CzEKG1%~7u+fZXAkh3PdrQ$m6x#-!<U2AK=T_h6kF(*#U|@Y6uS<T1AD=I%tXb@mi>078klkYGzD&M>!6;IIwoK;%<QU`wA>}?S*kVT62!1^&|@xcn3!%?)KRzEq!PUx#!1yfZ24OZL18(DY83=rJJAzx330Vz>j0cEs!V$Z-oH{(Ox6KT3urd@8$2uJd}Fn9D-xZlF}1v=22fF3E7qD`#U&|GvixdaZVnqcq(zdXK5v!fDla}qa!Ju%&oFn^H4>Jje@4u8rHZR4O{mW2O=h8*=}2l$Omd@%vS!(caJx*Iu(nZTN=S1GtHFd$)>bd!c_Pq)ZKnvFLG6!F3gf^Ps7jqZKWdYw?2x=frtwemx};5;m-|_lwk(B&+P$h3F(KrhRHcx1f*0}x7coC}T(Q9b*bqW1o*hORl2`^ebDq$I5k03;z+k*sUS_qf>ZP4@)}5wDnT7TaXE~h;;d|II6A4<zc79nmkPQl39Bg+`i&QMZ&|M&rNpQxcfuvXq@aP)N{?IO8mf=XrjM#s*-`(F=)rRqnavf`WA*+OCc@7gE;FnHuhlT%GMPx2PUT8nKX`z4)$EvXCk!$uLs|hC);u2hyBm*r)y{l34a%2ddjpoU>t5p+xKpBXyfH~$NP+hazt{%XygGJ?-amxrLr$D31so}$A3N}IMwSr_|2-MdUV%#*t+W_On%`9`1(3I?$i~+I?==%p)Gpc;9XB&!WhH^xy^%FGIKg<JIr}A$Y^Kw9OAo_X2K%_$yDQjFk=@DIRYYXlv5Vx7gr#Z?z6^63=pikj8bQR>lGl*G9qEw+x>AZ;uM|m23LC3U}fg7L{dL`cUqKDI@6^BsntExm)0U#$RYB=#RHiMMP8wrIZMf+80OHM(hWV~`NoSyu+4r$=?IiLhjDyU)a)6Q_AzKX@E;;<1JnG_wg#m2`ue?3!Pfzlga(v}b<o$qq)BkCL;p4(0-ksAxHeFN|^unL!}?+`;9t+N$glIIbGlk#+Qk{@i4f;_qUXf!{@#Yvz`DtbW-kqqhjgoNRUvTd}kD^tD?7M-kBfRHf#MOzK=>L~z5VZk>Cq)Cxvs*-kHsspxpqS4qZPrYJSiXT&51Rw=H%P@i{I%?d($?95RterYcbP-J^ktiIf=C??prqtG>$uh&1PnZN`PKuBye!Z7#;lOe+k#K(>EhEKHwag@$;wJ{0gWEx?EJJh1q=PGlVO<A|DVR=AAVX(RTgl5%LkUS9C^rxgkSf_t>$rrPsFf<vCGsMBRN)eMTt4GEb%e;MN{yrGuE62Z%83frL{uf?3E>=Ji>)9LK%!(z1{m5WW^tv1StdlsrdlIBCG4|2)L610Jk5z1`iO`eCdn_COO~h_%CtB9Dp+cnl*GIc##PIy+vP-&Y73`>2$qS2wDz_~=BuG5?P$-M)mdjwEo<4Gma!}9?B|dOnO_7JFS8D*doO@KtAGY+S*t6_Ug}a5Kn2Ql%`xVc=5jiDkv&oWg_BXV4W&sUxJaG{MmQnhK&iQ%T@BeUyen2;(=*WAwZ@L89U(pXgVe4r>i1Gbu9i8$Y52(`aa|+a({9QX4OVH|qFxnL2MIOEcb4_qnsfukwA*;OmJq1VOnQ!wM~qtTVMmME3O<|0+Q`+&VHHXO$x>EJ!F+4hw3Dc4Z<<i^*mblE>=m&VYM=3QWY45pzBVu(ZzJXqVZtvWR7|R=!AfgNPGUklxqZ=y2-MOF+W*i@N2qO_%wkubQ$9?`x<0AJ1|?hO$1bNcOkM74UjMGiq#ydoDB-B4ALQ^P`JITIu{=qGf*L{$T}eD~YE!y*m{~(ldAT#zl+NjB%6qS77mX7l^0=qIb`G^>Jgq}cGIz~T-&7HWFm?3>cj)0^FD8UK<v;azgKN*Aqbg-b1qzmbbA^kYCVGp9oV+%3q>#t)kqvZq7r7mQI-_wZ#$XENP2`msx3+zgR5`8MQ=%?OiqVvM3gSzS2x+|7DCj9Y{FK5w=k2Rbq^tMUZY6o`yT^x*<G1d=8GPV<1wVWKiY0RgnD2s$QM>EfP8>fRe?0ky5PsHrYe!K*%Ygnzm!AF)u#i~3')).decode('utf-8'))
_ACTIONS_6C12S_4Q_FIRST_YARN = json.loads(zlib.decompress(base64.b85decode('c-rk<O>Y}nlKd|^>mX7TDeX;dbJoVFTZSYLG20*-4eSgCSj--J=C;`Xz8*^?t12TSBlEqI+g{%YimH0wFEcVS^5_3K`|Gd2{rxY$o&DR-XFq&=fA{v654Vp`A0M`7`}4EE{rcbk`HxS3`SkJczy9`LfBEO9&p)5Nd;j^b+J_%L{`r^NpWgp?dv|tz_U3+fcD^)UKfc>;KMelxxZS?}^!4uD_V(%Qd^7p_$L-zyPiN<g<Ig`l+`s+!=IQhw>;3+J&xalR@czvoKYlp9X));A&u6>s<J0H1{&fHF^zQSg<5!ap<AHeG-rb$vdO3aT;c<gkfrboUd-^n;3e<qf>)hFcJv_GL^PDV3eSP^AdDn-#+c#TpJW+oR{{Y@LX*YT6%fAfA)3oFBcR!sL!>F$>Gv)j&9O3Ql^!=yhar?A=m@cB}cjMIqm+o@9h#v1hP8X3~oPYS&&KP|&=^dL&J2>M3o{Z9|e{XJImgeC{&pUI__0(LRhReS6Fbcz8h0_K0ADSGn6U+)GZ+RJeFlK|{Ff(R<qtDpOxYMB<J$JhEPD5y?$yt{R;cx?+!97~}*)r;aHnQl@i6`&SQhhAtZ{m3bL-=ySfH{ihO&`SLJB}YdoxP9fLvG+s<KFV%mtWFJ@B4f@;axg#_}{^sx;{7j@C6<_xm7M5Yce=Y6BkIIr%un-%=Uft7EJ9C@>63*^l8DH`@6gCo2Os?uzh%XfA{`B#%DsO!7INcu|&%6m}w3UxAvet?jAZiB9k9GSNYXGVFCWG*MDMur+r-2z1z_KYqUv#d1uVWfe{WCZpF_4#t7UKxK}SrJ7p&GJ`8&s^)Vbk;MgY&Qs%0_PtgO}SfEeg1DQu4+K&zXsNdwG1LY5@Wcw-`i2CO7{1Z>7&Gl7)r&9A0z5}rBPyV;H1>?PMaT8)%#_dZzF0@n$Z1&1__4lXsf0}&l0~2b6@#{sCO@MG@(b8b|TH6iBz#Qjt4vmAtEg0DWjYyqzFLbdF5X|V_8O5uSVe6;kx@}az%QBCqwgPyIH~-;{pqUUQ>x2vsH`?MyQ+yhrX({}Vz+7}hx*X7Om3BS(r%>9r1Dt(-?DxkeAt~Q_Nr&n|EZqsp2bR`V<;-mIbu?_G=<y}6khb7qWOr2zlpLazX+MdG!;o#_24i=+GdAyTAO7TZtQ9XBbVv8}#RxPSs$*Y@Lo^(V7J7gk92-A85&@b(5I*R~jy=CM>C6Co<Txn9k&3Yl0FI27-D!;;2IUm3ln4FvM0BYP-v>PnIXZkGSkS9$YQh!6!}h_J<MiD^`2N^di03LYl3spy{dvDzyXi_teOxQ*#a4QJdbr*Fuzh&=GhhcwaU*t%!45fZU+i13kT}LPZb_Hm(oR2<^H!7|KMTh#VHr;Gt9DE&5yfCZr`=pu)6n1;VpKWMhzGNp*2nR~@s^Gsr{S=NJ9e-QF&DLC<gv-&n2tbk6?pwlef`|bjwAEj&Pu@3UR#8ICNQTnkE`H(vytPz$C<uV)M}l<eXd^7Q1Q_NyVG7?^=TtM+@pP#1lkq<n7ZE)zEZhX7yvQ21b6rMcb~IVpbho%$CnxUbUwZnB7rAgJQc1hvxm;%q#A0OJ*Lg&(n=PY4ytzn$TsX@a^xYeL1)0u0ZBi-FZtdvFp~FDxojm=s40M|`yFjWBOCV(fh!42HJ{4x<F*i11Wg1e=IK)ftV5vRfPVxG#^$Y%7y&!y=tP^I4VAsX#u|M}jtn?|EV4U|J=b_tz_XZGsdE`a>q-i0I%oy~7Z^5M#l{s(5lvfM^H7Q+o9VP%3}xroo7`c55<Ih!u^O$?&I||vh32I5b!4t_lt4W}fO8&a{hpT-qUCH|l8PA7Qzj{|IZF|x0n_!)vwAJ25RU&b=mcMDZ3Y!wOkLTha9xTdl{7-_d+q5U4tZNdJ!Mtn*0Jln;>OZ6Pyc7R&1Sbcx!*yHCVwj?va-8B{7`ZPL4Vy&6+28OS??SQ4U4uLneE}(reykZ`%!W;m?a5DS7P-Efp{|p$HVpbytnWFJ$mIdvmw{dlLUes$|QmB+;Y#nv68g`tcSK&8e49rU~vs}1)K}by=dpyEgWybK(U7r{PF$WAIF{$^pnuB1b@b&%g1;1ag1(a$cF-J$4#DyyB2a46c0}!?IfCGSybFMbwZdalPnrdIu*@cP(g4At^DJ_G5MsZr`n)TZL?^{Na#6TRY{!{Fc#d#Y@Zs=Q;vL|l+%v#6<RGP;0-xra-vZR>Ay0<T6g9VC6&-sLF_Ej>M7;0fMEj1HyE5#n{fj<x1u=djtbd1c9RXG7KXF>FfqZ|D{T#M1o+2zj>B1=TH2H{giW9gk93RY6*P}|FqJq-!tu<0Xv1P`E7)i_PGUdT79@A$R}RmJ9Izpv0mTp)Q_CYOvM}wb269^fjgUXEM~A99!EibS{+M}hvPt|uN~#DkIjRP^bRi%Syd?+4D6R1v+l&3{`1N0aXSH_t<EwtL#VNl#p)Y&VJHTfU`JE;$rFSGmvaI2tyZeO5n~RXfJa21OMUK2=!3j=&#a#%{2*^~E<GktkR6957xDf0b9>#|4TI$!AaysdlqPD`z3dBc1Ufnhhum>TmBoS^!U<@6}Gb2!DEb{oE64|4jO}Mv~*NH{FX&hB^@(RhaDK9Wi%w{-81IH=JrV^8j(R?&1yb$1&8UME3Vk|g8tF9^gnHx%rkgAJBr-OU)(kxqvIjR#KlW6JsziLd0R-C+=VJ;ir0-=!4;@mAxF9DG)(d5-g${a#u6mnN*_Gc<Od#}(eV9m|#^mQMtS8LVpbg;Vf4{EJ)j=IbJ?A(Q(&0X%xKtu&U82auOk%_rP%}jzaRzNsD6>dOXxlP70j+WKX!7c>+8CSAm6>j!zBFRd3<UyZ>)e2Tdn{;K>2d!{aX-q1ld<YTKjuP6@t3bo;YIePzYOL9Rm6{D0C7KrV&8!~|259&aQQl{cR5ik3KrMkGIHh9R@J71X>suSYkonDwe$1Ah1NrOI4PG2gENvqA=ditt#lGOW(#Rm*{D5s@5SqBP*EZ&H<)V+9c-i;~iQdV{&Z(_GpQWy?_XW-X=m=UhgayPi6RT}!$x^<E8%CR^k};!tkID5l`rm5jNE(mYMmQS6wN6-uZZ}Y$r_4heslD3k<Qh!F8xF)em|M#J0@QT5*K2f!BuXkWs|!t{qIoo494)JL(O7&2IB}?rp>^cd&J1|5$9FX4(L1f9j7JUv`?`!0Pzh9Xfc6KFQ>2Fn;}U6Nq-NkRaGJrwKNVJU@i!Ry$h5tueOh{5YNdKiNZf9%;%9x9PRS9=OK;~d3*?Wri_+NWv78MuIA-UdfW#G$Qx5#>WRR03&?63?O2o*ML^c_@6>!@NAP~C`<)ruF5LRTE^c<n;51Ol^pb)iQ2%9X(Xpq$qF6C)Y@1JT75SkIrkTA9#5=w)$RTT{}b)XqbfT|5tFdl|R5RR{si>@3%!JSOR{6Twx&8aO`nZ(|2g#=WT=JmnG!c8#>W`nFA1;^!;tEr%ddVP8J>vCU^o`4DSc3g9^r8&&LqhOOwOj4Cq7-$q=EF}&HIDmkq0e(e%PV$?KTpGc7XincY1`WZ#6%V1}1|U>Y3f^j3N=*uK^!*e#W7AEKp_WYPP~jQeU0l)*ed@S67KzotE|&B>@&1>pr|^Lk&$3kOyB>Mr{B{}RrnO^k-Rpf5`>mCMmP)2=0C^<wzz*O~PZ%c)_;h0B5X0BPA;ST^j*2t|Ulnwjjwc&A;)H5aRX4x6PWyE-uLs=8IwGJ1M>}|VcC~~a^|qV3btV-?kM<uwSk$r&kkNCFFmBu^_(=^|h<K`c&`M*86~=K__$Bjs+?0Zxd1BW?$83t!%JjqO!y%!#Nr-L%E=W;08OUj{BoA6CP7IkZ_lcZCvc0nz^*nl6RG*V5cbdmqNHs&=A{!_QDiZvw$%6+~{zAtr3w`(ZzJO9-5<gbz8^H~-**A%ZfUnSCBgiKik5BDn#$jNNB<R;1=oppewJkpATXH_I+f(6?JTGF$EY84s#5bh-pV81?3TvbcF!^kZ;AEA?79|8p%@V*+5pjsyOq4Bag}ag*Q<qhjK0G>L2+z6XUVX_;cYTm?^`|cbF!as)Q4j`T4MJ!Eg%Xi_5Ig8uZipp`H1i68_hkSU!bEAU#|*QZ@c2_ir<|9fER1UYPgRGa0zNciSWGcT<9)KtP!e{cJP*5oIM;!O@wo*K&cy2y|15}JWRtC0Tt9_>)=Vd3PU~p|lKYjEw9=ecU`NHg>>_C+S(Sn*k4#c-lhXE#ia`cM(#7zTjADH5V&7KdgL#Qz)h|cUrB(G(Jalr6Y7cKxAWU_VB&%455~(9E=KF}`l7xRrrwFwLr?62<Re|Ja?NsKY)hGnA2zJ%cWc)$8moVBEQ8X)MZqn<n!U7DNTt#qMVj|k_K}O3g^%8{wkNWu&jeb)mGnJ?2{b0m{&}1)S1{*)w;~bR(Zr1+zLf8O`$jku*1ny^ow4U<81o{BJa*C7yMZ$%-UNZWT%+x59?6Q-Y2$GA!B8}6mll?p60GdNB3UHXaBp)A@oaRJk&G8Q{^~w7=%BqHFe9b3)UY5krXH=9_7M3nCo~dkZ`f^`LQ&H`l&LtVNOrsVlewr^q>DLJ!Bn#1N4!X~-twrCpvM<1x)D^DmwHOs9vWGpxmYkwFB6hM&1t4iekw@`V#fW{$v%<r{S@-IVlZ?@7QA3I0GO^2naK<Jfynr>iwh{?KM6^=@cyNM^Pjo7vL;~$P(Nol#@{jtwCPQB;_~NpkOV&`%;kCW7zWy2HVj<fxh|~&X_9lOhSR*;5d5OEJ61wdr<$0I^!=6ORYr7lx0dg6J9LW^*a0U{$T?$%eT-8NX+1xiJ5zkZq9A|!1n_*20AmVESudTp{vxli@)=9Z})ElN)dRQ+cZTl@Uiu^Jp63QS^A5%O8wEmEok=<O#m<%@#OID>sc}>TW$RaZ81oNsAJbFpPi4q!6k=P&>6D}VyuEuJK<~hco$QsFUNBdYnV>#73O)p8Q>I@pnHUwFIyx7bzr{Z{6=NA+$b|)mp1r>5@jL-OB+DO@QJfgnMNPwnR8|5sE;*=}<)#5s{04au?*6#4>L-pR(lw&A#MV(=AJDO_aJfdB3D6f$^r?PtS(F;PK0YR3+Zl2giX;v>YQoYu4phN>n6^Q+)$ELgzb!m|BD0g%iKS0c|Nn01Fha0hn;ND=1YN(?th+VQVV6UmD=<<&H84t^gB8*8>e<)fm42#%zG{eGuQv}<trL*y~f4CUldqc&{4LC+GniLsOzRm9@VWPlh#rFkImB{2CD>2v5V5&<nG(bVXYXb6@Ea5~~RH)=|ql|_C%c<&FQm~<M@|nIwsL(J8n9neq6HsfL%k!LL5@|ffg6Q+`A*i7Y`cmOVfXC2eW*$3x?op}%0a6|Z%+Q%|`>-trtXa`Z(S@O9u_}i-bTZO{v0jRMBaMcUtffqz4%z!VwaQlj(nx@4KIH+&+VU9$QhI*u4KPDLlxUFgmyWsCLA4`Z6T$`by0pyCQm=?zNG@>(CKR(j#1xI#gIS6`D#rwax=nawneSdeEt%3Q%j);#YuPul_+i3r%=pJ}KBA-&6;=lG6?bZlJ2m8hJbSPRjlF30j%{09deYDpUKy`>g;*zFfm$KKYr1r!Cu=1xx-~yhCBeT|VmI5kl3!B-!cHcw>?retixU>+90-!t@rp#*$=S*83du><U}PlOvMwQY4%PCxV{2MvZRzpxuv?1y3UZ<(^>%q)V0VkLY(|%gpd@=dY1IPYQBazXRi*wV!y>#DCKey7rc6iyGZ7(3SW!t{&}Ei@PcB=n7D-T%FFWqnC88GNi;mF~hjbmBM6orr*=M8$q7BRfj2u*P|C2R-nW#QT!;4^5*yZHGzFMR$!>LiS2&~-{-gT1FVtSgGlO2n^U8Lrz$k6f*VU_uznkK8B^OhBo^vmk-%ZN?fr9W}YxMPV8BNdra%3TWt&dMAy?2)>0B%8?6@&+FHno=8JFU`NJ^{}N)C~;#%mB^k;^u_~R^yP`JeNr+=>QDl{wexYAWOF%LwoJ8Il@dQ`T8QAY#ku-3K3<3&YX{9*e+@v@7gW6r#4cVRmP&FpU^Jy%P16;_OymzQtEDz7WhS&iQVMcNaot?@mTb&)QPQkcOG)SF+7+v3`h+c~#&uA8Shm)R#XNW#Bi)b4tImX6J^AD5?O&+-5$!JD^X5_T9Q-l0Uj#EiDjO0NNy_A6=)5&ZDRO|$covnSBzo$kl5@awdty-f67@=-S*gMa$uAi%Q?B3-7l^Mu%4c@iR|VCUN~J`Z$JE6aB;IQ$4RM9f`>7;?lv+-dlF}R9GzO6y;m`JSJ1_SY9T~f+Bgzr;!;`U#cwW_%A|hTxx++RTv+Nu-v1Un@bG_t@q(?;U9FWJT^evvbs|+m$St^n8>R^kmWVj$bZwrN%ag#Y>AtNDE-6^QJl?82jZaN~sM>ib<Z-k<@iuQFpX^aM;;l4zs7GzC<IsaS{Xy#dCN!sje&r#PXjksR-ZE=-2N5dPEi!{cP)6*kJjODme^<^i;C%o0O+;o{A{vEZGSiwfZ*7J{O&pK+yK!@<=@={Tn8W8?cN>gN(d7r+0-1IA;^Mz<r5^Aj|AQu^Zm=YZUZK?m7i|Hr4x(LARius9MS5Iq+WtV2guAEhd=4U+$Ms1@wYgKPszA!H`M89Z6EjE<UXLO4;^PcH&IU>c%35-ruc3}40^q8;Hlgh|B;Q@-oI{q_h*Ldz>N<o90Rn+KAl!2}(6U&T1mf6>&QAJ^49XFv$-uTUl!POXAsk|n8+K5GFD8WwD_><#2qA&(U0Mv@yG36~2n9`~wIat5O=8cUu>zGq?PM~7xg}dFH%aWv{7}}w89fcdfHZ8)i@jQs3;-Kvb+L;8OkN+zpD#$RkAe6l0RZ&=MI<;A!i({jNSyDlZB}(p4z|BRpM8iyAy-nXD>iTmrHzmBppgTRH*p?lN&a|S)2{X&YY6t;vtmTaM=h6-LF%n?ANFzv6`NwZwv0N@_?90Z?2N&fycEZoO3sF!AXOK}<5~`!@_6)VBL(5;+O=Tz3Yt%23>NCL{MvPq)Ct<b%)XXvri7Fl*HB(uwoeWIYQeZRrTA4f`MSqH)x`DB{Ybp)U1$Y5E`vb9~Db^Ad)e6f?V|%j*V=fviqwi?;eu!c=XzH)(Y#6D!HaO9PEwq*32RVIYnedUJ&Yj04)GEHC*)FAE*Z97mX?hUJ6MzjR)27ZU+f|v06^utG>>Ry_H6;xcGw4;d;|!zD71mP%J}d<yIf*w3rd$HVi?3t!TUGQbzK1gfI)c$8PzN_8e7<&)GAFMt7P=2O|63uIF`OQSKqLf2BYlPuDC3$Jl1#K+1gXs;3aJ6m5~XXc<4w*Cp+M*>BlO2w?!m2El8silRE2fcv!H8{7ZlyY_`f2Y0az#^lk1fTTMJLE{JH~Q>;HRYz@Ru?T2Qki%qHg1vGO1Vol@aWPuC4p$_0k5H$IoQ9f}7EU}cfoRDW^}OyJp6tB$Fv6-j!MA}*^A>wVRwN3>*CupL9;g!o3HD@Z8I*e9hmC5)3urjB^n_4!>U=2yyl)yya#+}I^TA8G>6MW<ZXSV@QAo9sT)*$X$Rl*mOX!8I-ts>=&7fzzBsaYMS5roELYv*M?wCwM5iT;;1$8Y?|^qgiCR&oj-Ul&>1=Sn*2kU{RJQ@v3*iInz(H-YhNSpoKDL+kR{{isUex^Wmv2$$8YP)P$vk-2=l#EH8knh^6(<ues2<36_og<iIs|5(C%)%*)#yKRxrkWWs8`E?(})T}cj`UFKYVO=Fw|-e^NTyqmgAf?8ih<FAj_+(lFILr-%r&JoNg?rGH`f+>Ez!iP7#Djdc|MF)FV2z6^R(z!mHG73&1L@(Z_9C>T4?uEqOq%t8PwaCvqFFHe7-Ica{*$Z<gjj7nrYJ%6DQf0kV;hXOXvyO=@=Y+gs#%!ukc~~f`Z^|rwosQmB`IBKcax}+Q5yWWxUnO@|7M0T>Q{TcVR!Af?Gd%+~eQ|cker3pWW#I>PBKju3_F*aFrLDW5Uc(6oLV{KkgRampQ<>o0K>(PkuX%&p#Ai&@INBu8Q3CM;;EPom0hcO~Ly}g`xmK}*0WmU0<N}}sVWSnN^%zo+UQCfqXE!7rvv^2UIm%@XIMc+wbWWiYUQ1^Fdh4&OIOXQKsOr8{eM>4Y*o$<{c~o}Q>Bu`x3M2y|E2b(^b~~xKqge2jdcI=K?sRA@BDw~r4w#RK4n@0(|M>u+B*G8ZrNFgCTrok<$V_Y%B?m5hs{&e5EzFxlqOIY<emZ9!?w@kAim=OTIFO{$dCXM1@-WO*9lQxnV4A+|-6h)1%IO_l^!{GvGR2%^`yz}ChT^~UNE@$~5}kS}C?0xI$0i)_a%ph9wb`p{XUbYLm@mH*EA=WNG8Jlc_H5z~D9}uT-L%^_v;Tmw11>01a!MpzFzHEcvqJiT15#LHU21<Mli2lAttG-{i#jo5SIkvWcX-AqxyD+GGy@4EdZ8#M&`S|qOP&sJxWjc?Q>j$5wxTH7s**d+^Sgs8FKLO;ye@qSH3PZ&qN3MUDoIemVkFrovKkqQ$w`5Xy!_xkP?ut^O2#^|N-0YVtx|?t=yl)gBwmt+%;rziQ;WD<J><&;%AnH6xYBAACu5n3EEj#QY6{6hCOFqpD3i$`xK>=IWl!>K8!l`>Wld?&yf48luK3D=7gVp4BsB%RBe2k$J72HK<0)@!rLxdrPI{Uwv~Hu7v2+7Hk|CuEJK)@n1ELr9@dyL~FpE@!V3AT#mDpl3L6HdE_P(_)MBts^wSgj+<qB)1NSKL&s;}KNFix)|TA>mvvyKDntt5p>C8M*l*TNOoT%QC$eIUB7MgRdXfsk8dF9R6k&xeS^M~&hcHDyUatn`xKyCAh9fBx&BS~{EgRcbx^40zO=R}`OQ9G765hzzuJHhhQb%q=<=S&6Jp8T17LBQyp|!GYy6X$2G#<*B!#^WCz>j;GX;4!3Jr@R@zss^?Og>Q!%)0>mGzN9RCljL#@>7(KZcZxW?c_xiaLF}8Mnw(FWmzX@}gD*wDwt~a#?dBQQdDQ!tq5~n<yM9jdiWu55a8X+gT)g@)dQv{4H%#2v@T&1gJlYrGSU<5mRgQ{IIiM8dp7;{`1OE3hNXnun#DY>d-w)-207h#|=h=>>7QeeEY6xmYKNrYbJW!S~5wy=p<+8rVeew8Zp)M(yDcBmFZXs(mXj!rhOT3uKgu3*QE>9JvC*J!ZBJP*$fu{;jd(ka)z)w62AtRd9zD(n*BcP38K+U^`1A5gUi(w|mgMRb1kxl>hU3fOEX7O>^|14QVy$&YVgl=65@P%BDR{Ldh>5guQ|8!Z9U&A)Dy*0iS5SA#0HOFdh5;}A=RUt;7@|9_=;av^$c;dh}h27}8;XfFiflmvCBb~AymGSZXb5`gJ$jYw#q%wDbDtW1AY+0&}#g=EnJ@428M&lr4MXnq=HQgP;y2f1n!FrpzeCfbMWJa4ffeS}@NjR0*Qw*XR5zgeb3F+K%bTGy3?Z??l}4VQxGf=w&Y!xjlxJ|VI&VSWt!sEwc!PokbN0=nAkSA`@tAE3J;N>!xkbST3}mHVj1A}Ge)dMd*Jp<3LBQaqWue_MH`WhFr|ptS{IS$v`9*Hp1guDg-Ff<8Nq=C#xKUh9~s8AM1_S83-fe=)WVgKE<wAQlGR)U!rK6+n&4&k#hll(RB>kiJpQlC`E=ah~*aur5(Au2yOF`s~IU0F4TzOj4aGAex(=o7AW>4AQ_krpLn$6v}T>-p{XCcK#gao$1Nb@QZ4JWqIQB<#5|fG5d`*SQ><8Z(3OKi^Uu)z{BWX!US=`4J@ZQe-)|OEfHBCPOCwS4B%T+zTj-2Tth8ta+-7p=W@7LS$I(<Hzbx0*OlA}AFM?g4|5Kq+qKu;Nr>ClWD8bJAfC1HcB<lll3Ws>jHGl1D0sb9<p28!Loy-?qk2_Kx{Dc5jWPgs;z8X7c9ID-DD0pYR;XR7Jnxpv_=HvG^Ey}{1tVg>1(;3LNJ1?Iv_4Iuh!gduFj%fEB?t}Cym(qph|GCh%QPcBn7HXPWpTok<lNZOBHzr_V=huaGpNYC2Kx%EhtPJBMDxxWT;nbn<B0_eDa(5Z`xd46GK4f0jsecI1x5sMm%wjy524g50_&fiY3%;8|2W>3hfxrUM)%;I&}zO0vd~U)hO1T=(2bYIsKfkBk-$3|<7@~?@Icuh&1sssErr%5DFXzaB$kC)EafcBjhX`3k1e(I(nh~+^yT+gakvGJ;35<eRLq01CBCJEJ7CPFTwa(#Q%Zos&NyyV=xA>HMy1Dz92MP?Do7>fLde93h61Q8S*Ec@Z-F6@$vL6Alevyc;nyxHlXBKJGJ4{D-69!U(P>K72+pQM7T3L!sFX^v4v$EZ=~G-wsr*$`Jd_Y%=vNUskOM){z*vhfpsj|Rxp6&9*-s?Cs8C_xa%x=FJl%u%N?Li7T{1sXiEM8LppPzMmmw5bkv+*MJmxzIl2?>~n8!!q3BM3$Ht`jd@+@#uG}+K#`?Da4xRsivtE>a-u-xs2A{93Ah2AmwM`DsF-$a5H1lnOxyL^tsnr&mEO{v_8P6r~B+j~xz36>($NmRL;)<ioTD$h{IWdzX-ex^^Zh(tXvF1j!6H{cdAi<D7p*`!G&h>M_-l^R@vWRb<P2~@JH>DwrkDwq6{Dl%mu4+|9p9PT&=M-AEuu+l0MHcWsSGJvC2daG4K2urSm!(FC?RERiC6^W{p1*l`pM<8Tb^a@Im1^;Pr(jrBMRgzS*BqpSq)Y`EbTanx<zhJ9%e(l=f<X6>-DJ>qJTFBm_K+Tj=l53R!+6Z;l`4CehAX}I#!~7HLe5BeJRJmtIre32`6aFgX;&3xP5J^mnXL}87T!&Jf8L5FIPyHH+5ubbMVDYlmjy^`PuwRMtFxsm9aQpZuh#4Jz6(sPa&|8ZiJii6Cj(Q{LS81}3Cis|XGicVxi6njVN50p9p61=O2Q&=oZ%tNC_m+WICC99Gx=W*G7hiVRo<F2oHjRhT0$Mj9)#XYkRM_Yc2cpIN9?x(m5{x@?Sw#66C4(vz`=U2PkutE;yf&WbR<dv-{enPR-&z3KuB*s*Wbwo!PpW)zs)Do|YA?nQWZC~50jX@V7&<B>h#)#-<QCBrIiZeZ%{m@LI=mMAEwj7u&JK`u&}UT1+T1-l@F69(Gm|IvT9H=_dV3s+N{Ss(Fkxx2G+<HcD^<54XL@cco!F!g_a8h-PJuoamr4dzIHoa*=O(m_iwn}FD5xt`Vp`X4WVJ`P!EaJWusS@H2Oo!OmTpRP*uvwgI==Y$js4*LMvU|X1Oz2vetL31EC2Z6*vy1w|F1>A|39U3_`m')).decode('utf-8'))
_ACTIONS_6C12S_4Q_SECOND_YARN = json.loads(zlib.decompress(base64.b85decode('c-rk<O>Y}nlKd|^>mX7TDeX;dbJoVFTZSYLG20*-4eSgCSj--J=C;`Xz8*^?t12TSBlEqI+g{%YimH0wFEcVS^5_3K`|Gd2{rxY$o&DR-XFq&=fA{v654Vp`A0M`7`}4EE{rcbk`HxS3`SkJczy9`LfBEO9&p)5Nd;j^b+J_%L{`r^NpWgp?dv|tz_U3+fcD^)UKfc>;KMelxxZS?}^!4uD_V(%Qd^7p_$L-zyPiN<g<Ig`l+`s+!=IQhw>;3+J&xalR@czvoKYlp9X));A&u6>s<J0H1{&fHF^zQSg<5!ap<AHeG-rb$vdO3aT;c<gkfrboUd-^n;3e<qf>)hFcJv_GL^PDV3eSP^AdDn-#+c#TpJW+oR{{Y@LX*YT6%fAfA)3oFBcR!sL!>F$>Gv)j&9O3Ql^!=yhar?A=m@cB}cjMIqm+o@9h#v1hP8X3~oPYS&&KP|&=^dL&J2>M3o{Z9|e{XJImgeC{&pUI__0(LRhReS6Fbcz8h0_K0ADSGn6U+)GZ+RJeFlK|{Ff(R<qtDpOxYMB<J$JhEPD5y?$yt{R;cx?+!97~}*)r;aHnQl@i6`&SQhhAtZ{m3bL-=ySfH{ihO&`SLJB}YdoxP9fLvG+s<KFV%mtWFJ@B4f@;axg#_}{^sx;{7j@C6<_xm7M5Yce=Y6BkIIr%un-%=Uft7EJ9C@>63*^l8DH`@6gCo2Os?uzh%XfA{`B#%DsO!7INcu|&%6m}w3UxAvet?jAZiB9k9GSNYXGVFCWG*MDMur+r-2z1z_KYqUv#d1uVWfe{WCZpF_4#t7UKxK}SrJ7p&GJ`8&s^)Vbk;MgY&Qs%0_PtgO}SfEeg1DQu4+K&zXsNdwG1LY5@Wcw-`i2CO7{1Z>7&Gl7)r&9A0z5}rBPyV;H1>?PMaT8)%#_dZzF0@n$Z1&1__4lXsf0}&l0~2b6@#{sCO@MG@(b8b|TH6iBz#Qjt4vmAtEg0DWjYyqzFLbdF5X|V_8O5uSVe6;kx@}az%QBCqwgPyIH~-;{pqUUQ>x2vsH`?MyQ+yhrX({}Vz+7}hx*X7Om3BS(r%>9r1Dt(-?DxkeAt~Q_Nr&n|EZqsp2bR`V<;-mIbu?_G=<y}6khb7qWOr2zlpLazX+MdG!;o#_24i=+GdAyTAO7TZtQ9XBbVv8}#RxPSs$*Y@Lo^(V7J7gk92-A85&@b(5I*R~jy=CM>C6Co<Txn9k&3Yl0FI27-D!;;2IUm3ln4FvM0BYP-v>PnIXZkGSkS9$YQh!6!}h_J<MiD^`2N^di03LYl3spy{dvDzyXi_teOxQ*#a4QJdbr*Fuzh&=GhhcwaU*t%!45fZU+i13kT}LPZb_Hm(oR2<^H!7|KMTh#VHr;Gt9DE&5yfCZr`=pu)6n1;VpKWMhzGNp*2nR~@s^Gsr{S=NJ9e-QF&DLC<gv-&n2tbk6?pwlef`|bjwAEj&Pu@3UR#8ICNQTnkE`H(vytPz$C<uV)M}l<eXd^7Q1Q_NyVG7?^=TtM+@pP#1lkq<n7ZE)zEZhX7yvQ21b6rMcb~IVpbho%$CnxUbUwZnB7rAgJQc1hvxm;%q#A0OJ*Lg&(n=PY4ytzn$TsX@a^xYeL1)0u0ZBi-FZtdvFp~FDxojm=s40M|`yFjWBOCV(fh!42HJ{4x<F*i11Wg1e=IK)ftV5vRfPVxG#^$Y%7y&!y=tP^I4VAsX#u|M}jtn?|EV4U|J=b_tz_XZGsdE`a>q-i0I%oy~7Z^5M#l{s(5lvfM^H7Q+o9VP%3}xroo7`c55<Ih!u^O$?&I||vh32I5b!4t_lt4W}fO8&a{hpT-qUCH|l8PA7Qzj{|IZF|x0n_!)vwAJ25RU&b=mcMDZ3Y!wOkLTha9xTdl{7-_d+q5U4tZNdJ!Mtn*0Jln;>OZ6Pyc7R&1Sbcx!*yHCVwj?va-8B{7`ZPL4Vy&6+28OS??SQ4U4uLneE}(reykZ`%!W;m?a5DS7P-Efp{|p$HVpbytnWFJ$mIdvmw{dlLUes$|QmB+;Y#nv68g`tcSK&8e49rU~vs}1)K}by=dpyEgWybK(U7r{PF$WAIF{$^pnuB1b@b&%g1;1ag1(a$cF-J$4#DyyB2a46c0}!?IfCGSybFMbwZdalPnrdIu*@cP(g4At^DJ_G5MsZr`n)TZL?^{Na#6TRY{!{Fc#d#Y@Zs=Q;vL|l+%v#6<RGP;0-xra-vZR>Ay0<T6g9VC6&-sLF_Ej>M7;0fMEj1HyE5#n{fj<x1u=djtbd1c9RXG7KXF>FfqZ|D{T#M1o+2zj>B1=TH2H{giW9gk93RY6*P}|FqJq-!tu<0Xv1P`E7)i_PGUdT79@A$R}RmJ9Izpv0mTp)Q_CYOvM}wb269^fjgUXEM~A99!EibS{+M}hvPt|uN~#DkIjRP^bRi%Syd?+4D6R1v+l&3{`1N0aXSH_t<EwtL#VNl#p)Y&VJHTfU`JE;$rFSGmvaI2tyZeO5n~RXfJa21OMUK2=!3j=&#a#%{2*^~E<GktkR6957xDf0b9>#|4TI$!AaysdlqPD`z3dBc1Ufnhhum>TmBoS^!U<@6}Gb2!DEb{oE64|4jO}Mv~*NH{FX&hB^@(RhaDK9Wi%w{-81IH=JrV^8j(R?&1yb$1&8UME3Vk|g8tF9^gnHx%rkgAJBr-OU)(kxqvIjR#KlW6JsziLd0R-C+=VJ;ir0-=!4;@mAxF9DG)(d5-g${a#u6mnN*_Gc<Od#}(eV9m|#^mQMtS8LVpbg;Vf4{EJ)j=IbJ?A(Q(&0X%xKtu&U82auOk%_rP%}jzaRzNsD6>dOXxlP70j+WKX!7c>+8CSAm6>j!zBFRd3<UyZ>)e2Tdn{;K>2d!{aX-q1ld<YTKjuP6@t3bo;YIePzYOL9Rm6{D0C7KrV&8!~|259&aQQl{cR5ik3KrMkGIHh9R@J71X>suSYkonDwe$1Ah1NrOI4PG2gENvqA=ditt#lGOW(#Rm*{D5s@5SqBP*EZ&H<)V+9c-i;~iQdV{&Z(_GpQWy?_XW-X=m=UhgayPi6RT}!$x^<E8%CR^k};!tkID5l`rm5jNE(mYMmQS6wN6-uZZ}Y$r_4heslD3k<Qh!F8xF)em|M#J0@QT5*K2f!BuXkWs|!t{qIoo494)JL(O7&2IB}?rp>^cd&J1|5$9FX4(L1f9j7JUv`?`!0Pzh9Xfc6KFQ>2Fn;}U6Nq-NkRaGJrwKNVJU@i!Ry$h5tueOh{5YNdKiNZf9%;%9x9PRS9=OK;~d3*?Wri_+NWv78MuIA-UdfW#G$Qx5#>WRR03&?63?O2o*ML^c_@6>!@NAP~C`<)ruF5LRTE^c<n;51Ol^pb)iQ2%9X(Xpq$qF6C)Y@1JT75SkIrkTA9#5=w)$RTT{}b)XqbfT|5tFdl|R5RR{si>@3%!JSOR{6Twx&8aO`nZ(|2g#=WT=JmnG!c8#>W`nFA1;^!;tEr%ddVP8J>vCU^o`4DSc3g9^r8&&LqhOOwOj4Cq7-$q=EF}&HIDmkq0e(e%PV$?KTpGc7XincY1`WZ#6%V1}1|U>Y3f^j3N=*uK^!*e#W7AEKp_WYPP~jQeU0l)*ed@S67KzotE|&B>@&1>pr|^Lk&$3kOyB>Mr{B{}RrnO^k-Rpf5`>mCMmP)2=0C^<wzz*O~PZ%c)_;h0B5X0BPA;ST^j*2t|Ulnwjjwc&A;)H5aRX4x6PWyE-uLs=8IwGJ1M>}|VcC~~a^|qV3btV-?kM<uwSk$r&kkNCFFmBu^_(=^|h<K`c&`M*86~=K__$Bjs+?0Zxd1BW?$83t!%JjqO!y%!#Nr-L%E=W;08OUj{BoA6CP7IkZ_lcZCvc0nz^*nl6RG*V5cbdmqNHs&=A{!_QDiZvw$%6+~{zAtr3w`(ZzJO9-5<gbz8^H~-**A%ZfUnSCBgiKik5BDn#$jNNB<R;1=oppewJkpATXH_I+f(6?JTGF$EY84s#5bh-pV81?3TvbcF!^kZ;AEA?79|8p%@V*+5pjsyOq4Bag}ag*Q<qhjK0G>L2+z6XUVX_;cYTm?^`|cbF!as)Q4j`T4MJ!Eg%Xi_5Ig8uZipp`H1i68_hkSU!bEAU#|*QZ@c2_ir<|9fER1UYPgRGa0zNciSWGcT<9)KtP!e{cJP*5oIM;!O@wo*K&cy2y|15}JWRtC0Tt9_>)=Vd3PU~p|lKYjEw9=ecU`NHg>>_C+S(Sn*k4#c-lhXE#ia`cM(#7zTjADH5V&7KdgL#Qz)h|cUrB(G(Jalr6Y7cKxAWU_VB&%455~(9E=KF}`l7xRrrwFwLr?62<Re|Ja?NsKY)hGnA2zJ%cWc)$8moVBEQ8X)MZqn<n!U7DNTt#qMVj|k_K}O3g^%8{wkNWu&jeb)mGnJ?2{b0m{&}1)S1{*)w;~bR(Zr1+zLf8O`$jku*1ny^ow4U<81o{BJa*C7yMZ$%-UNZWT%+x59?6Q-Y2$GA!B8}6mll?p60GdNB3UHXaBp)A@oaRJk&G8Q{^~w7=%BqHFe9b3)UY5krXH=9_7M3nCo~dkZ`f^`LQ&H`l&LtVNOrsVlewr^q>DLJ!Bn#1N4!X~-twrCpvM<1x)D^DmwHOs9vWGpxmYkwFB6hM&1t4iekw@`V#fW{$v%<r{S@-IVlZ?@7QA3I0GO^2naK<Jfynr>iwh{?KM6^=@cyNM^Pjo7vL;~$P(Nol#@{jtwCPQB;_~NpkOV&`%;kCW7zWy2HVj<fxh|~&X_9lOhSR*;5d5OEJ61wdr<$0I^!=6ORYr7lx0dg6J9LW^*a0U{$T?$%eT-8NX+1xiJ5zkZq9A|!1n_*20AmVESudTp{vxli@)=9Z})ElN)dRQ+cZTl@Uiu^Jp63QS^A5%O8wEmEok=<O#m<%@#OID>sc}>TW$RaZ81oNsAJbFpPi4q!6k=P&>6D}VyuEuJK<~hco$QsFUNBdYnV>#73O)p8Q>I@pnHUwFIyx7bzr{Z{6=NA+$b|)mp1r>5@jL-OB+DO@QJfgnMNPwnR8|5sE;*=}<)#5s{04au?*6#4>L-pR(lw&A#MV(=AJDO_aJfdB3D6f$^r?PtS(F;PK0YR3+Zl2giX;v>YQoYu4phN>n6^Q+)$ELgzb!m|BD0g%iKS0c|Nn01Fha0hn;ND=1YN(?th+VQVV6UmD=<<&H84t^gB8*8>e<)fm42#%zG{eGuQv}<trL*y~f4CUldqc&{4LC+GniLsOzRm9@VWPlh#rFkImB{2CD>2v5V5&<nG(bVXYXb6@Ea5~~RH)=|ql|_C%c<&FQm~<M@|nIwsL(J8n9neq6HsfL%k!LL5@|ffg6Q+`A*i7Y`cmOVfXC2eW*$3x?op}%0a6|Z%+Q%|`>-trtXa`Z(S@O9u_}i-bTZO{v0jRMBaMcUtffqz4%z!VwaQlj(nx@4KIH+&+VU9$QhI*u4KPDLlxUFgmyWsCLA4`Z6T$`by0pyCQm=?zNG@>(CKR(j#1xI#gIS6`D#rwax=nawneSdeEt%3Q%j);#YuPul_+i3r%=pJ}KBA-&6;=lG6?bZlJ2m8hJbSPRjlF30j%{09deYDpUKy`>g;*zFfm$KKYr1r!Cu=1xx-~yhCBeT|VmI5kl3!B-!cHcw>?retixU>+90-!t@rp#*$=S*83du><U}PlOvMwQY4%PCxV{2MvZRzpxuv?1y3UZ<(^>%q)V0VkLY(|%gpd@=dY1IPYQBazXRi*wV!y>#DCKey7rc6iyGZ7(3SW!t{&}Ei@PcB=n7D-T%FFWqnC88GNi;mF~hjbmBM6orr*=M8$q7BRfj2u*P|C2R-nW#QT!;4^5*yZHGzFMR$!>LiS2&~-{-gT1FVtSgGlO2n^U8Lrz$k6f*VU_uznkK8B^OhBo^vmk-%ZN?fr9W}YxMPV8BNdra%3TWt&dMAy?2)>0B%8?6@&+FHno=8JFU`NJ^{}N)C~;#%mB^k;^u_~R^yP`JeNr+=>QDl{wexYAWOF%LwoJ8Il@dQ`T8QAY#ku-3K3<3&YX{9*e+@v@7gW6r#4cVRmP&FpU^Jy%P16;_OymzQtEDz7WhS&iQVMcNaot?@mTb&)QPQkcOG)SF+7+v3`h+c~#&uA8Shm)R#XNW#Bi)b4tImX6J^AD5?O&+-5$!JD^X5_T9Q-l0Uj#EiDjO0NNy_A6=)5&ZDRO|$covnSBzo$kl5@awdty-f67@=-S*gMa$uAi%Q?B3-7l^Mu%4c@iR|VCUN~J`Z$JE6aB;IQ$4RM9f`>7;?lv+-dlF}R9GzO6y;m`JSJ1_SY9T~f+Bgzr;!;`U#cwW_%A|hTxx++RTv+Nu-v1Un@bG_t@q(?;U9FWJT^evvbs|+m$St^n8>R^kmWVj$bZwrN%ag#Y>AtNDE-6^QJl?82jZaN~sM>ib<Z-k<@iuQFpX^aM;;l4zs7GzC<IsaS{Xy#dCN!sje&r#PXjksR-ZE=-2N5dPEi!{cP)6*kJjODme^<^i;C%o0O+;o{A{vEZGSiwfZ*7J{O&pK+yK!@<=@={Tn8W8?cN>gN(d7r+0-1IA;^Mz<r5^Aj|AQu^Zm=YZUZK?m7i|Hr4x(LARius9MS5Iq+WtV2guAEhd=4U+$Ms1@wYgKPszA!H`M89Z6EjE<UXLO4;^PcH&IU>c%35-ruc3}40^q8;Hlgh|B;Q@-oI{q_h*Ldz>N<o90Rn+KAl!2}(6U&T1mf6>&QAJ^49XFv$-uTUl!POXAsk|n8+K5GFD8WwD_><#2qA&(U0Mv@yG36~2n9`~wIat5O=8cUu>zGq?PM~7xg}dFH%aWv{7}}w89fcdfHZ8)i@jQs3;-Kvb+L;8OkN+zpD#$RkAe6l0RZ&=MI<;A!i({jNSyDlZB}(p4z|BRpM8iyAy-nXD>iTmrHzmBppgTRH*p?lN&a|S)2{X&YY6t;vtmTaM=h6-LF%n?ANFzv6`NwZwv0N@_?90Z?2N&fycEZoO3sF!AXOK}<5~`!@_6)VBL(5;+O=Tz3Yt%23>NCL{MvPq)Ct<b%)XXvri7Fl*HB(uwoeWIYQeZRrTA4f`MSqH)x`DB{Ybp)U1$Y5E`vb9~Db^Ad)e6f?V|%j*V=fviqwi?;eu!c=XzH)(Y#6D!HaO9PEwq*32RVIYnedUJ&Yj04)GEHC*)FAE*Z97mX?hUJ6MzjR)27ZU+f|v06^utG>>Ry_H6;xcGw4;d;|!zD71mP%J}d<yIf*w3rd$HVi?3t!TUGQbzK1gfI)c$8PzN_8e7<&)GAFMt7P=2O|63uIF`OQSKqLf2BYlPuDC3$Jl1#K+1gXs;3aJ6m5~XXc<4w*Cp+M*>BlO2w?!m2El8silRE2fcv!H8{7ZlyY_`f2Y0az#^lk1fTTMJLE{JH~Q>;HRYz@Ru?T2Qki%qHg1vGO1Vol@aWPuC4p$_0k5H$IoQ9f}7EU}cfoRDW^}OyJp6tB$Fv6-j!MA}*^A>wVRwN3>*CupL9;g!o3HD@Z8I*e9hmC5)3urjB^n_4!>U=2yyl)yya#+}I^TA8G>6MW<ZXSV@QAo9sT)*$X$Rl*mOX!8I-ts>=&7fzzBsaYMS5roELYv*M?wCwM5iT;;1$8Y?|^qgiCR&oj-Ul&>1=Sn*2kU{RJQ@v3*iInz(H-YhNSpoKDL+kR{{isUex^Wmv2$$8YP)P$vk-2=l#EH8knh^6(<ues2<36_og<iIs|5(C%)%*)#yKRxrkWWs8`E?(})T}cj`UFKYVO=Fw|-e^NTyqmgAf?8ih<FAj_+(lFILr-%r&JoNg?rGH`f+>Ez!iP7#Djdc|MF)FV2z6^R(z!mHG73&1L@(Z_9C>T4?uEqOq%t8PwaCvqFFHe7-Ica{*$Z<gjj7nrYJ%6DQf0kV;hXOXvyO=@=Y+gs#%!ukc~~f`Z^|rwosQmB`IBKcax}+Q5yWWxUnO@|7M0T>Q{TcVR!Af?Gd%+~eQ|cker3pWW#I>PBKju3_F*aFrLDW5Uc(6oLV{KkgRampQ<>o0K>(PkuX%&p#Ai&@INBu8Q3CM;;EPom0hcO~Ly}g`xmK}*0WmU0<N}}sVWSnN^%zo+UQCfqXE!7rvv^2UIm%@XIMc+wbWWiYUQ1^Fdh4&OIOXQKsOr8{eM>4Y*o$<{c~o}Q>Bu`x3M2y|E2b(^b~~xKqge2jdcI=K?sRA@BDw~r4w#RK4n@0(|M>u+B*G8ZrNFgCTrok<$V_Y%B?m5hs{&e5EzFxlqOIY<emZ9!?w@kAim=OTIFO{$dCXM1@-WO*9lQxnV4A+|-6h)1%IO_l^!{GvGR2%^`yz}ChT^~UNE@$~5}kS}C?0xI$0i)_a%ph9wb`p{XUbYLm@mH*EA=WNG8Jlc_H5z~D9}uT-L%^_v;Tmw11>01a!MpzFzHEcvqJiT15#LHU21<Mli2lAttG-{i#jo5SIkvWcX-AqxyD+GGy@4EdZ8#M&`S|qOP&sJxWjc?Q>j$5wxTH7s**d+^Sgs8FKLO;ye@qSH3PZ&qN3MUDoIemVkFrovKkqQ$w`5Xy!_xkP?ut^O2#^|N-0YVtx|?t=yl)gBwmt+%;rziQ;WD<J><&;%AnH6xYBAACu5n3EEj#QY6{6hCOFqpD3i$`xK>=IWl!>K8!l`>Wld?&yf48luK3D=7gVp4BsB%RBe2k$J72HK<0)@!rLxdrPI{Uwv~Hu7v2+7Hk|CuEJK)@n1ELr9@dyL~FpE@!V3AT#mDpl3L6HdE_P(_)MBts^wSgj+<qB)1NSKL&s;}KNFix)|TA>mvvyKDntt5p>C8M*l*TNOoT%QC$eIUB7MgRdXfsk8dF9R6k&xeS^M~&hcHDyUatn`xKyCAh9fBx&BS~{EgRcbx^40zO=R}`OQ9G765hzzuJHhhQb%q=<=S&6Jp8T17LBQyp|!GYy6X$2G#<*B!#^WCz>j;GX;4!3Jr@R@zss^?Og>Q!%)0>mGzN9RCljL#@>7(KZcZxW?c_xiaLF}8Mnw(FWmzX@}gD*wDwt~a#?dBQQdDQ!tq5~n<yM9jdiWu55a8X+gT)g@)dQv{4H%#2v@T&1gJlYrGSU<5mRgQ{IIiM8dp7;{`1OE3hNXnun#DY>d-w)-207h#|=h=>>7QeeEY6xmYKNrYbJW!S~5wy=p<+8rVeew8Zp)M(yDcBmFZXs(mXj!rhOT3uKgu3*QE>9JvC*J!ZBJP*$fu{;jd(ka)z)w62AtRd9zD(n*BcP38K+U^`1A5gUi(w|mgMRb1kxl>hU3fOEX7O>^|14QVy$&YVgl=65@P%BDR{Ldh>5guQ|8!Z9U&A)Dy*0iS5SA#0HOFdh5;}A=RUt;7@|9_=;av^$c;dh}h27}8;XfFiflmvCBb~AymGSZXb5`gJ$jYw#q%wDbDtW1AY+0&}#g=EnJ@428M&lr4MXnq=HQgP;y2f1n!FrpzeCfbMWJa4ffeS}@NjR0*Qw*XR5zgeb3F+K%bTGy3?Z??l}4VQxGf=w&Y!xjlxJ|VI&VSWt!sEwc!PokbN0=nAkSA`@tAE3J;N>!xkbST3}mHVj1A}Ge)dMd*Jp<3LBQaqWue_MH`WhFr|ptS{IS$v`9*Hp1guDg-Ff<8Nq=C#xKUh9~s8AM1_S83-fe=)WVgKE<wAQlGR)U!rK6+n&4&k#hll(RB>kiJpQlC`E=ah~*aur5(Au2yOF`s~IU0F4TzOj4aGAex(=o7AW>4AQ_krpLn$6v}T>-p{XCcK#gao$1Nb@QZ4JWqIQB<#5|fG5d`*SQ><8Z(3OKi^Uu)z{BWX!US=`4J@ZQe-)|OEfHBCPOCwS4B%T+zTj-2Tth8ta+-7p=W@7LS$I(<Hzbx0*OlA}AFM?g4|5Kq+qKu;Nr>ClWD8bJAfC1HcB<lll3Ws>jHGl1D0sb9<p28!Loy-?qk2_Kx{Dc5jWPgs;z8X7c9ID-DD0pYR;XR7Jnxpv_=HvG^Ey}{1tVg>1(;3LNJ1?Iv_4Iuh!gduFj%fEB?t}Cym(qph|GCh%QPcBn7HXPWpTok<lNZOBHzr_V=huaGpNYC2Kx%EhtPJBMDxxWT;nbn<B0_eDa(5Z`xd46GK4f0jsecI1x5sMm%wjy524g50_&fiY3%;8|2W>3hfxrUM)%;I&}zO0vd~U)hO1T=(2bYIsKfkBk-$3|<7@~?@Icuh&1sssErr%5DFXzaB$kC)EafcBjhX`3k1e(I(nh~+^yT+gakvGJ;35<eRLq01CBCJEJ7CPFTwa(#Q%Zos&NyyV=xA>HMy1Dz92MP?Do7>fLde93h61Q8S*Ec@Z-F6@$vL6Alevyc;nyxHlXBKJGJ4{D-69!U(P>K72+pQM7T3L!sFX^v4v$EZ=~G-wsr*$`Jd_Y%=vNUskOM){z*vhfpsj|Rxp6&9*-s?Cs8C_xa%x=FJl%u%N?Li7T{1sXiEM8LppPzMmmw5bkv+*MJmxzIl2?>~n8!!q3BM3$Ht`jd@+@#uG}+K#`?Da4xRsivtE>a-u-xs2A{93Ah2AmwM`DsF-$a5H1lnOxyL^tsnr&mEO{v_8P6r~B+j~xz36>($NmRL;)<ioTD$h{IWdzX-ex^^Zh(tXvF1j!6H{cdAi<D7p*`!G&h>M_-l^R@vWRb<P2~@JH>DwrkDwq6{Dl%mu4+|9p9PT&=M-AEuu+l0MHcWsSGJvC2daG4K2urSm!(FC?RERiC6^W{p1*l`pM<8Tb^a@Im1^;Pr(jrBMRgzS*BqpSq)Y`EbTanx<zhJ9%e(l=f<X6>-DJ>qJTFBm_K+Tj=l53R!+6Z;l`4CehAX}I#!~7HLe5BeJRJmtIre32`6aFgX;&3xP5J^mnXL}87T!&Jf8L5FIPyHH+5ubbMVDYlmjy^`PuwRMtFxsm9aQpZuh#4Jz6(sPa&|8ZiJii6Cj(Q{LS81}3Cis|XGicVxi6njVN50p9p61=O2Q&=oZ%tNC_m+WICC99Gx=W*G7hiVRo<F2oHjRhT0$Mj9)#XYkRM_Yc2cpIN9?x(m5{x@?Sw#66C4(vz`=U2PkutE;yf&WbR<dv-{enPR-&z3KuB*s*Wbwo!PpW)zs)Do|YA?nQWZC~50jX@V7&<B>h#)#-<QCBrIiZeZ%{m@LI=mMAEwj7u&JK`u&}UT1+T1-l@F69(Gm|IvT9H=_dV3s+N{Ss(Fkxx2G+<HcD^<54XL@cco!F!g_a8h-PJuoamr4dzIHoa*=O(m_iwn}FD5xt`Vp`X4WVJ`P!EaJWusS@H2Oo!OmTpRP*uvwgI==Y$js4*LMvU|X1Oz2vetL31EC2Z6*vy1w|F1>A|39U3_`m')).decode('utf-8'))
_LEGACY_ACTIONS_10C4S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<O>ZMva{Mnk>mX93K77-3bKQ;Aj2cq+66=957{F^7FxH2$Z-)Q7dnK}1RWC9!GV@W=jCEsE?5g+uG9x1+fBv77fBW^fzyIyGlYjd8<cDvcZ$JL><>uk*xBJb><LSx2|N5W*`d{Dw^8MrAfBo%0{`TMBKmUC4>GRWHwGTgh`|B?^KYjl3=Jw?D<ip+e<aF75{qSkC`7-*$!)EjG``6n~o13pEr<b#@f85;O{d97=7=Hfc{_f+q4_^=e<Kpr0e^199`||n2pTB)MylFA&+s`N4&BNEHw*GW?|Mk<;r{SyFhv`5(Y;JE4Z#|#Cb^o~0t3X4>uRVO4PX%hg>~-es!5$7Rd76{Oq_4YQk#~K$z4@@Q#uN2t{~y5HX6+_#-TjyGcsA{L`tGO0Vwm)GH&e#X+!5Z~%-?@l9yeb%_wz+G|8BZ^;L=^r7tzDrxA`J!7w4b;u`?#$%zDSBvK^f10MAD0(7z8iyQR7R(eut6bv-nfhv8~px*vt{uiWVZ`wvYH*a^)FCU4n|Js7jma5OX4{zjj%-MG`Cn>=^E^A1DUPLr`N7sBBNHiLPz^0Q^q1#M)}q2o{9zNPwD%HR0&2!?QX!hkvQ=1m{O;T^+=?`Q7=`Vbqq!?;%-y!$1c^uEuh6W*l*`~N$7Q`hIZA70_Hvs>lduqK_uG;o3RdFuRZjcnf+Z^7IiAwO-*h(0a&aCdvV`SA6ZKW*;6e!l(uFVi!j)8M6F5?CVXcN}RB_P6$^J?0)79Ff_NjjMe97_b1}^!g9X@4Szzym#x`e?^-Fn0Jl&I5NV)!p-;@z!-sh0{3dSv_obx@58vaULV~71de^cAZ4x!{Nz25jRpGTK9G3?qWxI#N9`sj9VmNHCEHioK-4$)=bv~wHP=@Gp4`VlZ#m#R0OS7f$krJ2H-8J95ZlskU+8hJsY-CO7dEWlpVt3r^1TmisFezG=M4kfR%j3BDU80D!Q$Ufz56?a)JVr6yK1FFGGjjsZyg<2@w-!Od!=)sAw<Y}=}w^cYsuK47j0%(xE*6ckrAiKYk$COqLv3S84~swUGxXk&&5UwdgTm;4;e-d-Z_-@#{sV1AN&5;-{E6*0IP?oV@KX$2;YUA)?om}2+6naZai4#&T05c(rXOhDYXEkXAxyUkQgczX+MdoR~=b)!5d@q>E`|~R>%6?_yM#)jAEmq8v2qPqVZT%C<g7|v@ytmOi%(+_@ECRdwy$d(2-F!49a+<d^iN)E0bk+Sfl$vIYd0=K|eeZT{YwPjSO@hgPC(Q=zRv>kclw24{m8v?`FgMW2+$1+OwQ?zq@+c?yWJk#>B@(#I)KOF%MtwZ?->d?(hE!ESVI-<aWq>JEUPQyTeVafkq=1k4HeGUJ!%|-JJn5at=jh?@}9C$O2EtGO@<i$rx*jAxs=pDXov;!*HehkJE6r{f#`@w3z(bG1OV|PUa(!Tm@FYLtj5PGiwo|PtOg_gjm~Kju74iu6E>c8JO^BbiDV#)@y~yE+W{`x@gy&KPHY(AztR#2*gl9$E)H@Q(xT!V=~tYLn}s?;P&qB_9-m}npV3%?k4E_`S|f9ZR;KUdEDE;*V56cnS+cX(TTG%A8PAXkPY7Htc2I{FcBgs2V=>X0{aJKD)lxLQd7kI5G_8Y-q#WgRicOKzDtcA)kZ&Eq)b9@n@?%Hb7SR4#F_|T(|I^H)<lFdjyO}(#DelJ2z0)kZglj`Pm9bpV8e_)>4O4Jofbfzr_SUUU%)4snYYKXqAr5jvWry2ZW<d~`IZ;VSPh$FB4tW*bmj2Yj8_o@L{RoF$Tl_F0Ipwlo#|+W;!k@6WPIJ;<i-y<q+pyE=aI>V8M}UZcFaPM?roZpXH&ftNPz)lLu4s{_JR4oaWbkIaeN3qk&I?1zqDdKupLAbO!a(nmctref$%>R4PcX9e(J;{TU5}$Wr+{L_FKDNdf8@e$a%i9;0J%CnLRP|0vG_Mtq~gMw#)3fX8&R)4+XhN2b;h%$imGmZRM40G!TrNJm-`afH6;;ZIN*{U~4e^nL`!~sLu6_4?j!k-#=1mNd~W`JOVl4`xSD*`yjcCun$sa0bXNoBP5VBCKR?d0sL9W^GKv`fZMfZuyxAy8?LM|8f=;Vz^Eh69F;%PghDtmmD{hFrIgL{2)G8|x*R5WZ}9&3`S#Ddm1p@$?JxaIzY0jc+tSbPTZqtsgshL_HLK_pgGCpH6*zcXar(f^hLs4mydZ89%FhXgp@h`aW6Dv1Bl}>ckB#95C~2*E4vl0IdWZ`%K1zJjshArT8q0GZFm2s7B!MNaMSOVHoHH=jEo#)B<478)m0xR((qzoFrOmQShVK>ILiZ`SF`OB^Q~S#NTh2L=9N)x;Y{I$c8kxRXuhx-mKxZ%J(dzACD;``}tz*@9c;K{9XvLjK;uLmXX6*}FNN4Vf$2{eNv#0@2ard#N!*)2a$zfh;Rh2gek^0{4ky6d-0YQVG4Pu08M_2H|SJsI_ey1r^9m72bW{2mU6MAkevZ*`kuDi;t7%@ZA&z1BoewasutxVaI4W$lNk}#Pc->%|A2&?^(o=T~cb#$HOXExXhuOyIGD8W3`d#GX%LyPk)s`2$Q9R&sKp}uf9s!P<rca4fT%5t&@+WML<NFX)@_-2h?3>tzQQb$^(wR$r=KIg?!<er2!i5f?q3I$G`CT@;~7VJ!03!6Q)>OpJ63iY*H>o`F-6G-AL?-VA?gkmufDHV{ULVN|tsz?OE6uUVgo%RymhBBE)`cRz47id-f)Oibo2u!fI(5&~tdf%SMK_+CMKkfU1Iw)@@Y~HqwhRubLb<EdA-O%k_C4w%ulEpzX0i?^vn$U4FHw&2lD#sxQs;8XL7(<-;P#HcOAV1QW6A#y+hm>^#AgjW*$xoHUpmIT;)+c6IH*GD$q;hk~{o3(c#8_)JQ;R>Eoj17I*1~kL+v|YG>*T01axap|B+Jc!(R~|>xVva8IvWU&HB2xB?OmKbCfKtK-D`gY@P)%yFzAk(dew#~R{kYLqo?qcVkpE$5s{FazcvBO#lm0nY#q6>uXtV<jwko(;xQBcC(szktlD$k#?=}7t**&qozAuUWs-?Wnn_bv31N?fplJ`hd0W`4aUIxa(ml>chD#21?)G_Lr;%9!Q`ZKnJ#!uo3&>)YJG_4EC?-X-r64+NR&zvi*oL@s>hiXT(ka(6LhLYFbw+A4AP;QZ>%>|MO)>#$vz>G8uc1_ja^Qx9^QK2VN`^o?X+)(axzdA%Nj5)vB7B$5Ti~e7>*g@Dv`yW8b{%xnm+Zuy01;ZDo^c4vhz9-z{N^em9MT5zAeFiM3{`b-4rvmw=rZ~;Q~qmmrs~(Ex$1KXH;i)R4LnOSOjYBMvRd0XbewO)ZHpOOGDANA4&u-OZ&)?TG`p)S8CcdJYy?JpeL<M#j%Gz@g~WIs0_Ycdh^tyzS~i3YL9=Gw;)-E5G2O!^VkTEkSOic5rh3E;;=rQtwNCBS45@>RF4*=9FIf-Qf)p9HxGZ5ZhkHzLZMOr8zKZb>eq>~QhnQ%YqCn=OA*6R@`7&+&T8oNx&(EvM3Zl4+Mr$f9%n)8F%ScikmwnSPKQ`v!JB$Uy+{e@Q${j4JTI(l@ILxu0Bw3?{R?R_>z&stPtichvf^op+0M69KC3<2m!<XasTsaWU@i7>{cu<3-CIp<bLiMbaJVQprUKEXqvtW`6wU6VDI*9g%6bIS`kmMTGMV6~NPHY9~SO|!Ta^{X7JWMGhQ*8;g(xx1Kj(8uT(!qw8p3b6T)9z;9Fd~KP=haB}ipX~$X(eDtlRYmE4ci+nHKLf^!&qGvzgNfs4TumD4dIcuL%IU%*;Ug2F-OIYRN@@TSstG|XlhiD5uLOED;x6JDv)%TwKc%XKQL+)=9wsspB=M3;R)uM$DIg6a5Kq-W0g?3Td%JR+mF)~u?x6$+|d_MjKoMYfs;HKp~y{@mx4H4R2vez&M4I>$>5B8_l)!~?`W3^M=>*tTp<<DER0}h*Z#XhhP5hw7w-OxaV}bG9$FGo;((1&B)tCC7RmAoqJj@qd3H6U0-0hmp&}QB1QvhN-*=s?%w!aSA|^FK{jPWsP(2E%sa@zkt1SqZ1oholxBQH)<X|vbq3#eOh^|d+ay!Afofgp)$OspuASmxksx2Q;JegiL2}KA;P(hMyk?5sCIx<@xJdPjJig4SydQ23SrzgJ{y=1#z^J&?kKtUJE@t`SFY5!Z&191ZCY%!RrCIa#ynAut$9$gH4p=a9~q*t|Gg6fLLUG1gdVzup|ZdLoC)mrS(Q0iF|QAbItu!n273}hc98To8rMGrBbX~3plsp;S^oi0O6#!*_l`nu`S+-i<SOo+6$B63i|_1j|!@XQQ!^LK;<Fmeq9^BYW~R1+0AcAlLNgB}GJdK(Pf*9$?E@*0vpyk4E6Ec8H}b;>B$N6Uz3pUQj<ma7o1<DtM#Ds5nqDg(pNhCK(p#Y=~8Lc@IVSjkU`d1;|t3z9W7wtb+$1DOq}>VUCMrZbVD8ni=x7>?=Fh3t+T_+{7M%Q)Z}Zi=LHQ!9k6rU8j^nVG3(8X<5YIb?)P<{&NS=ZVo!AW;N3mbnvMN_z@Ryqt%kZ@N~GNIllrT}r7_N1LZWv{^+QeCjRRjGGu-_N<${SQ&o6Wd!Qs9KArgL^$0*qEG<9i@9tsmtfxnb>C?0_Ogpt_M)NNSWU1(F8mRKxXFruF;2F^X7Pp=JI&NKC=#_nq%O~hcXY&ff_sss-L95twZdoBjeys!r|UD}lhM120U&v82MP#Cb+9XhQe=-%{Zvns&KreNu_<4eq18j9eh8(>R`&pi_~>~DF6b4mxTwo_Q5#;<f^s5FStC+Wz!Rgc()e`=#Y%FDv4M7Y;B`tgSsf9vOeYFUIn`ZPhoou{@__iG)PcV&QlxpV7?XaqBfvtVPs_fF<`C29Kl2Qu9{qK(?bMQ_NJyGeeVt~j$9h5nk%$d7?)b;g{~YPjV%fXxm@WQXDtM&0c41v!))Mo(vL0EK&8vi2gU*bkt9Wqm+o^2+G<<{CYv-jnZ?;oSaoi@rPDiwhjYmv~#Fy6U4r`I3?rHRJEMgM9$3S!@5bXl%Ce9>g7sk$5zSTf{j;>z{$#X4p)9~&WiTBcNH(_bOD)HW}Gal5iJx(w_UWhVT_pl_jKs~*q)Y@q6Pp=4Rh?1OS$Ft~==WBN=-{CDNU;#_%<H@{rje5=NMQ(bOH)n1m2CW=!gFYp+pEF733*Wvccl7X(T2ea8-_pcJlF9;7&=)PBF#iGdf+`HKt<AmqQk)#2mjSq!#)Q48B%#Gvq=fB4qEAUU;yRZr??JFk3^nXdU}^(`N_z<4T(ig=ehsAlEk??GQh<Ujo-jS`JmNu0fB=il1L&*|6(lAd$(1BbW<)nHoz;Y7$O`8@gnibfh%#nn{x7Jv+BW6QFcttu`&AhVz^{-g3bgihouUBJN;BI0f*xMgy@igx9|YX!QN*H%lk5U}e^)ASiscCN?sHbdtzBX*9X8Gg@Oi8~3gl6N^ldCy5nqi;9lFywS?@BE*6QePc>+$3FInLED2ix^%pL&Qs3YU8NnIGpcYvr4ZYXxcfd}%}WF0;orQoZF>L-OW|8>iLah1ueM|g%=fa>Ci6Xe!yizsXYCxis+Ii}-9rZig1?%8X7CrJx1NFWjFJ%&mqUW1B>qL)F)8lo5hPi$fPQ9dYEf_Eo^Uo`y*{GQQe5)FrtkH(<T3QTKzBa+Y{6cP1{BM&XLE_L{0hCa*fhjmf2n}e1rB-qQe+n$+FnlI4b%hse*g6D4O8;?Q5maIttp}wfs;pS;-nco5`LqlZDv{FkdWdJdA8RYuN6C6T$LyR;dl|O3i1QlMIu}WMu2BSi0W2A@#*OpBZq_;X<GM4bFQ@+r0W$ZIhuX*{#5{ceW%?A!OL0T2+(YYIS=$Tp66+#N&e1#&La%qT;WhRAj$}tzD6eX4OqUDAN2-;B!3ouAVFHb2~`OwtphGVUiB`yIk^6W_T(7_wjy;=}Z$izlNdm+&SnxMoa5vT{KR#Z%ssk9y7X?iIhV3~K+TraugBUZOU^N!<!s+!^eK`cOYiRTijI-+4E_+=pbh&N0VlTi69@rIK%qNehJ9%#A0=|+<^G7U=L%_gfxcTHAUN9ZcC3MlR0R2f{^-#klWDq2kvwdIWcFoI+Lv4s0|N<;+=MIeoj!shUKb@$6vA`6cnp0thuE3BB_HCKYFqLMmAJ$9}QqiT7;)@SuMsYWT2h};kWZrxe((t_sJ>27C*F_ny@Xz$J&SasF0Uzw_&%7^1t{%lf-W@$&S2Misq&bLtv#Nlgk`fQUaH9HbJBS90Sr$XUU5~-3LF8*k2wM9r=qOYD~bHR3Ypl~IzAg9u)80=K!621H*4^N=s2p2laF{Boc8FfbD6bJIZf;f>fYo~>*3Xn3?DrHG|TgWtNZE?<?#67%3k+1+a%q_Pgsoii+ga$*-<9M~wDZJ7faoTaHnkrd`EJbUQ7!^ly`$UJappV&Yt)YHc+zGLIW2W%RslN8EQp7N|iU^I6)s`NrVt1K5`xxB`8z>s&r}kxCnla$_i%Zj?(lc3$lqA*SJU3^ahM)nh+6-~2fS;IU<8((>x1|gVm#W2(%tBq9DIw*_Tb4Q<QD5Q7>h}NhlFaAlRwokHMOwg#$2T-79u|e_L$fOgRH35r5}>%%!~z`lSy$58WhAqYk%U-^pHvG`o=nAzAvvJ2-e{U`LjGExe#K;jv;spEQl9@l*^OhRX+A-G=Vt=>t0^Ni!~QP+2sM7*Sk)ibNbEoZi&O?mND@&yU!Z=qWoER}LV7)!&Lw|5=mwkvrSijWJCQ~25vN{3If+>_Q{T8)A<B`h4wS%v8+j3&9$$5u3`Hf!SSq(|ktiIWPY3<U(qLxotX+yiMoz++7WkBM52sC?|Encp<=9?qqS>?CEf2C}DH>JM#iIb7S%OD#e4Lc7S|&GTt{77+QPh&vn*0nTeu6lWzm^`A<NtEcR?FG5x?0j{l%%VjGtc`SpNg2e9@TLs>@jQbv|>(ML$WI@jw}`vr-y@0^)nL-!!4&H?<=jajcKEgv4e{y%Tn2TJ0m~^3~LIJRDqnU@UuomOT(4bhiQgF+dh+IA1a~|uOk&9CGjgyDOx=TKwhKnm4#%yzPi*K11xy?E6P=}D|;PBYzlIfXbZKpUEgSMQqGigIa!AaAHXDNRn!*U9-oxdyTG&}_X`(Gw4_y*X%tC<@o{Tb6U#<W0zioFYl*$81*;|fVo0Y;<~4>YZ5g)b(E{7>_}dcBCNng7s+t<2U!}M(4sjw=$=vXPX=&J4X%T%-s`sbIv7!R)iOIUG5l1#=zLi#<Oh0KAX`Boh;VQT9)LLMSsb;9e&}Faa_M~E+Wa1=8)Yzk(bWxFv6DT8al7tFG47RrJz}CSF=tYHC1!)CoCaXljivUxq$Pd!jE6)&Qtif2aU2+z6E-M8)Y$(fj1eD*u<|OUQlW}q#O+b9PS@KG-?$5dJ$LRf?H~t!bNvfb5?i!)*c&Fr*dk@0{*HH$@P_o9qHA~7X)U@4nNwA)na>5k&8Bpr$V;xoet6lQ4q64itAZcaBDyh9F1Im=Yn$%nKZ0hCNAFI4te-e~fYK`-RUV!w}p(L9x68N(0rz~+vS23akacsVm?qdeT%(x5No$#bp2MSgf4)B@4;q5L8iJHa4Fxn#_w^W$?jB3Ovi95Mjr*UrLgC}x3l4Pb(&_W$h2Jw`Lkeb7w!Bg?#M7z`ZJaG5WcKR`4Jo+Z?lw&%1uq5h(lOkn{wI$0*vVcD@KDe?PWeF0`Bm>>UVgwM^=fx#vGDpqop%trY)!%$>&?zqwha?=W6S50OL(nHCJ#Z~orCMiS(h)B~AZ5rgXH+XAF&uyC3@|sTQuju=Vq(4<i%`O8#KRW}wUpQpx|Z^F2|RRwBR=LhJb{8e=7c2|N^R1%jFND=#{_fXesL$Ux`$E_RjS)qhzl<xXx!;>m|zp!@S0X295?Zu3YIDbkBmN7c&9HBjO+SJH4<Z*TOF_(0YP%j54RqR3yNgayir0!ofDS-pV$|X#h*X|e^4@)6VC#K2yrVJ4vv~&9MXNcehlD8tU`DoOOzAR6Y90g6j#Y9>L9Dpi_$kb)~HJ?S+lx`RN-W&Wwai+S#}vIf@O$4ixh>#-I<<-2zNq=ZzG^g*2#1pm|kUdYd5A)_lxC8^`S^A355(V2WO32`yd>r)k<|O>{&buC=oKlM`f|$NzO^Or*u-Z+KZG*qnU!7NaF0fMQPtb1J-0mppLnPckwhUb7-;B!h&k;2Bmx~umtzKp<%rCUx+YWUo)uPi?ocInjOmPrTQfR!qPvh+{P5=Y|A1P>_i1OMyM>RV(@4Pi`aRdsI#>*l(sJQsz%#$a^6Cd4RikpYN(W`aPAnbN_Lvb4uMb(oKXeGD2%(^1Y~=23@;|!rIh?6=7Uy#JHysI%Mnkb^_ZJ01O_=bA<W%(G+&9hwlWH&{y!+(D1#ZTc?L3DhZ$pNt?*Z;=HpVV`IxElMa@O+iq^{kHdQl}L%0QaJw0yk@7s--#*)zhA|AaXEo-D%syw|Sjn2qx@lxv|l&UH#j*wg6k9e}GkELlR1<2^IZ%mrLC)(0Jk%z{k%^7t>#se7UR!f&H#}+&;B26Q7L%GT2DmNt}_W>zFu^}Z#mC+>1&Y@<JljG-m8anyVLn58g)LR)JKkh4dEW?0=4jn)zt4tp&T(HAplw~$FrK>rCAfKA$7uZnClSv^Fu__4C#c6ZNLS^#CHMdesnIN^Bf~{ixMwOcwrHIh0kh3Ux>as7&QkIr_c1k(RQsTIY-ODU87YY|aiD9j~RSw*>=L6ngq+H(FGEc-}dDna3fyXJpanZ~pWtm0OA9*&QE41hZCxo7L=|+hlwmhQ*vHeSzZ;CYbcB>sa$1dX`2C5yt2wyCshn{pZ^OP}{1C}d;7)T_OY`s1VuOlUChEh8U<qk7!D6Js*Ti|-p3s+NHL9wu9q?^}zjoJwDE2UsW*+CK3CtIEueW+dN26qu4+SP(Y%(6(`($NI&PI@w3M+#PkNL$>Hq=pyx3W2B@^4+RP-SRy~&+l<O0e$MON(Uz)YO#=jF(F{qO@OXb@iNu1(@0#-ebA;udYGF&kJlx>0HJS5vaDW;smc3N#5N_eR!+x|z*W5LAjrk#3A?<QiHbw4Q+Z)}o;5n6HmQVRQcue`T8>jiP%QJw!<(vNm2$HKe|V3YNbIAA+rj>q9oFbl16a(rq*)E}mUEIdG0)6BP_E3K7P=Qj?u!Hus)aV1mEbS|Wb)+V$cdXRO313AZWIBGi~|*g-x!6^5m%u{@m9lvb369*m_-OoQr5MGEUu1?EUpoDxTX}Qbv+$bCs#*!S?30~YW(L=?M3(mr3_<+nbopgT$GQZt}bl16{uG&k;U_<vt+GqieW6<M--hSE?Qari*WLE>W#<Jst)qZ2Nd*DWArUnVNO-L(EM*Cp<=H9ca?iHpu}lItC>SNS|YoH#%HRekyY#+5Waq&?_yO?HRihova~6eCR?eC%WZLvk+2>(A13F%hzSvXEl~mwk>MnX4!Ta6?oiPT;4V@&gi;{pLq?e{+i1?!dES&}hzu{;wvm`ROfj>NWWCJK9>>S{HkbAFN*TFX&1kVkCixleA6?v(JEpGHfKI=x3+mBeOnKE(38m?zod+TiG@pyY)r@E+qbO&od0}{Zf|^u>6r@f_7nD=p5}x8uc-}M8aP9-~DR^u2^mtkxz^~{66O~wV+An7>i2h83$H0lZw8Au(c<6sGiey&k`!$uy809Qhw37EO;fT1@RZTE5l9AT|cN3^9NvfK8+(oN#GG(%$-dYbiGPe@|Id_U!=3uyOLW@i%%sqicIi^(~<uH+M=7(q30f?HQBO%<tQx8+U2*DF=X&%c=sXwOt$fO@=kUdFuTb4^s%5<Ww2O$^fq~P#kpte+PC_Us6>^EJ<fT}OV^8*4LCB3dAbQ1z$_{2~vRSz_AGq1>>!hJ~a_!?iOr8jZthXsSx!jf)*#XuArU7H-}@C1UQbtD6=9^<XMWz#Yus7MWWPQ`37VPkSNo?$sT#2GO?FQ&$$^N*<nP$&&g16*|Jy6g-vJrEVOlzOMavMKsoYq!{yD7TU*qFpSJ9P+LnS7D+6fFe|MPziC?W&R@jWowJXj_?s0cOtDN=+<$?nid8xXt7YLTkaV{QhDq14DQlSmkt}*44sSDNkvql6;7dt4G|@byqKe(bfcMS&^KB=CRB`4tz>E;N6;|xT9N!aq45_bjg)#WZfp=8XK>!zqGYJQ4hcb&8Sq2p!TE39%t%2|%>@dO<%riyoma0_MwUTrtXS>$mIcJw(_XHk&%gn#fvI^7zR5!Vwk4e7Eji_kylLA?1Q6Xc6*Kk{t0{_{gM-N-9<ay+cUEczZAB$AdqBCEPNWu_ua};#;3D8gnvcLkV(jK-p0nhHE*=xwT3>D+9;P4s^3l1nZwiHH0`fF18$OKuFVt%IWu}F@2O+eCv@Y}^v+&wxfdT3Ap*mUzXYwsIt8Zg+t(sdpDSpGnCDqa~6ONkX@kwq>)JuftphOY~x~Z<QsKxP3Ie*E#a8G?-+Mw0|iL1qPq-mv~v?)W?!5xFgH8R;`%NkhL=^Z1Hw|A#*(dsXDcGd78XJD1XD!?2DT{b&cd@1Y&B&v3Ot!@xi-uv<X?#mG_C4z;5jML={U6m}UKzL)uxCy-yyr4ZZkN!&Jz4v`-d;F0*@g=)SUh2zolYTN082gnjO2zu=z>6FE>d5qTcZ_HshIh{XL=FukXEH68f=dp($U*Y>f8tM+hX')).decode('utf-8'))
_LEGACY_ACTIONS_8C6S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<%WfRW5&RdPc~H-TL;A**dM(0SQJ^Rf*1}-1fY&f!tPgA74F9`javt4Xk&%&EHRN!ilLn(<cfBh!GBWbZf6o5)^KZZY^4r-TzMOsc`R4ZBPam&8J$%0J&o<|0fB*TPfBo0j|M~jy*Pnm;$1nf>`uWS*`<uuA)joXp`NyBGKivFqeS3C(_V#Xlc0Mb<{`9`@KMwxmQ{TV)`t|yKfBkTFzM6dfLw|es;q1KI|NP_q-Mi0k9}a(UvDy6heAuy%H*f#+`QzbD-Jow@&er{>hsU;lxVwLN|M+SD)#Sr?AU^fCw}-dRr*GXoZtyD5kl||&pQclR8ZddCIeV~&`<6V;NjK{2_E+RxA8)VU_SSf!{_Oq$ylv8M^49I249Bx*$K!V&4vS&b*X>LhKXXU8zn;GTusp6G`upi3ntnH4J#gvHri<v)-RJ2dDi`PX|KAy-ZzjECQ&|qqcz`FPbm-sP>+RCq{pe|D4!Rzi%foP$FWrs8@K^41f&GUj2keAm1(UaI#~zH?U^t2yD}STU*mm6M(2bru-Fb&0ET_p>mz{99fz4nZt^8~mbwL|hbm;h#w`-|Bmhw0LJc1$Io-kmJym`|HasQ6}hp%VvC-fmUaEEcPdGPj^bkf^CpH6s_4($GR@TR8Ebw9koV<)%D+^{B{!!&S#w0Y|EY>jN+XK%sO9w9$1%!oEEczbty+rNGI>HGfv;pX<{FXJ<z(cq<D5?CVXcN}RBcDMGRJ?0+TJ0g=G8&~;q6R-eJdi@9HciP8A-n(_}ze<|~n0JNwI55J&!p-;@z!-sh0{3dWv_obx@58XSULV~71de^cAZ4x!{Nz25jRpGTK9G3?qWxImkJ?R6I#BkYO17`Efv9ip&p+{W>Rew1cyb>Hz2$)O0F3*?BTHk@-~1(TLTpRFeWAy>rYgbBp4qVe_O$j-lka_CLoHO0J8u}+wnBM0k74v~0*ik=_3rNwQX?IQ?5dRx$&CH5f9v4Dir<}L+iN-(8bXAuSKSHpeyuV#=tY|u7H-FwP-Mhu^4cFTo2cbMOooI#Mi>17^>eXNf?hd;;X{UzgLevL{eFO}Z;$=<*jM;i9l&Z~>e!KY7{YfUr)3yGF+%d?y9*DNxpNx6lJpt_cuHLW(zA#%AV>_AinO0Z)oUGDcEKBC^Zxq&&sN9U-S`2tK#XFeq1yK)IYh&;sG%5?gHy&J_hf=9AcYV5zGF{sjSV_7s`i6294Q|T0r<*j*&WvCZcq*pPkGP}PefPE@O=XVUB_Ui91VJ(fj49#%;kein$$P5;oD<tL87H+Ic<M;`MBLnV`_<sk6pyH+8QyR9`3K#-}U$RKLSf8g)q4tGT#nqn6u_^6KkN+h;DNPH0l{asL<URFe9f>RQ4{lk%cVqbSx8VXq^nPrWnG+L6xfYvH!5Y(*4J2INR<<9&B1ner*`)tnyB#BamDLR=-1EKQ%LJ5u#5|4b6mD%Ug~R-UP08<Z&68@Mv_rZ-K3s3X@$#u%l(AT{GV#j!z+8=GX|tP(jD5;!IOt-2-DX*9t=`2AAOa?(X(6Ee4ua+yC57(AV?v-C5e!JNWasw}G#vqf;{n8AYNIXJtCn)~z5LyyIC3ujTzjh@c#dC9eeb56Dz%Z78Isi1{H}d`!KsB^auT9;W*)b?m4z`spHN5_(&FO5>fql^+pnB7jY&;n-Lc5z08=OpOx@s&_%4^W}7-qi=dzWVQhtX7ouP6maU40P-|-Cdc>!KFP$qJ(d-95zLnDQW3jxY;56MUNB=dY>tVPDb3N9!&?(xMGO!@*}EXy)Mx{^e%W=VqZNuj?G2Feb$OE;Kje^tabC<LlMOR={q*dZg&^JAG$YTZdMS_s1IYG~r2yIo=KtEssAk0Reej87G&}jFHP!>$K{UZs&nIU&tl<?1|De(UHreIpPCT+i1^ru=_z-NrmFuOIZB~Yyrz;D7@JE{26Z>8O1HiO3LgQR^nLXF+U(Dp8AUEk?5qJh!xS6G`ypoLuf^n1QoYDd?=83Z{GR_8U4Te8+$btdYxt{UiXDR)=M=CAJ;MJ5zASZmkKrVP2B)1FuAoVQ3E9`BA1agLi!qO&yKMQ#tiS!L{yVe<OjdK0=SJn^>woHFu)DdTn${%S$A)J`X?N`iF%I0|lTmx`j?k9L>@cwXf`={;7v;3s;mwu*S4M@J-(ogT}MCd?5)`#($MRbb6q6@<c9K5Y@`oPQfD-mpYLEI*kpA!s238|;Yl%oPi_Q6aa8p8!pQd;vI8p$N|5Eo{6l=!4mF*hnSmUAC4E!{RGfhDd*e0bJ5XJD>N)Tlhiku*>#zg8Nh$(U<Nn`M^_-z&C-?o)7MI5T*s_Lcd6Ip;)jd=nqC3Fn?`Wcp^UT1U14oxPYxtG9=(cyM8rj#b;?fzv{v6?Y<uQ`mT!l`kkEovAAx^OP%`MGbh0yN`7`Y=;w@9OgBxs^yJAq`q}~q*Sx|fS|$81~J04qbqpf3+qH7zta?|j^UmIv%~Yw2|YI!+0>nN*Ii{+jF=(m=Sun(Kg=V-R;KL9hEfM>k}#PcU#{Xq2&?>&o=T~cb#$HOCpOpuuOyIGD8W3`d#J@A_ASn{sD{_ecoY<{hx)?ds4h|e-Zm=YD9gzrXzOdbAc5Er;F}eGF=z;KNF8aB((29d_?#C@k$V!_Bx)RaDik<%inuu%TCg*1Eo}DGS`S(qR;aICTE_{xnLrX}d8aU8CKQW_NU4A%72+#ERz)HRrr6C1>9ptYHk8Rc(uc}ve1=x#Pn}a3L|}rQLbJXN*0=3>9ArZF`P05HsDpAcVe_(WG;A(}tYf||>V|IbDiL(Kl`IaD2_UUDbwbC<+$>=Fs~m?MsGf2{V+?WXLuL4Efc!{fPCQ(P9#X9v09h5bO@6K<22~g2DScvwb<@@|Oe!~*+^-$JMU1u9W@_<Av-1Ww+gg||c6$}@c%2+oM(#xtnPj;cFuHGJ5qB4DMP~!yv4#nTpuOFjO@ckk(7p0U0ADzK1%vLmsh4GlV&Pv>G<ph8DTYGyiim{V{G|z4cAdZG**bD%U-7&!98d1m#U>N}C(szktlDwihSeF{t*+5yoz9i}Wt53Ynn_bv31N?fplJ`hdF$-exD4zw=^p1J!zBkBcY7Y#X=GNw)Rlp1&zy(D0<xIp4lg$i#iVGq6hw#3YK~|Q%Mf=?UEUT^I_FwOh#f|&&PZ(r<bmG3POP<1Bom-E+d0?%8cKC22X06>Z+g_DWC*mA22^TVLU^xYlFg7FN#CV27dS5SvRMozaZ`7oT^HT-CL6IQAb*^b%4t;9>qa7_z___DBl01LNDV2?&F86B59g3B0gErAFEeGpMrW&jU7Bk@mw3adN8Z4*WW!Wd4k^2}j7P_LH{8aUuqHD!1mGy{JKzngMxADNc1<RhH3+@HjIUo1=E<X36Iwwro{s?fg&yLnS5_^X!iXQ;3oL);6xR&1j_EEou`{`bLKnafnEnwrjRVWVS3R|pG^7qP;$Yb?yl6dy3zB8n;<6;l92PP`xZMsYN-M@g_@R;YB4YAoiWZrVi;&(`3z=!_*IHDpdwzyhRvN`!G+I+>iH7h>nMKm;xB#4n{;@F+-(oB@=02XbSMFeyzO{a$h{GJ~Ns>QW(W)sN5}2nW6*xE|YcLMo9AKJynTeLz%l^w@doCTQ=J;3);6A8fQxgo%S)qD<N}ekt;xCHY#G7EcN`e+c95WF14@nP{^PeOg)vGPn3Oca`q=O+KILawJeiSh!l}tq@)RLQW96I8BD8<&@G>vpV6`OZA4~J1ITtBaley_-V2hvvphBVpq;?S_oQIaGo^L!Y;tH$pYvOxoKghWkv;O&sEz{++tLI9YpV#h3Tw&WzE&mA;1K1kx{TBMbY_+$}Cg3Q_yV09oE#|jfpl*Uh>!<Og-bIjvDgrU5dq{Ok3sNAd9*M;rI>C)I0z;)cu7eI^_BVE%(??V%Eq)3X=L?W^0oL;v~Hzw@dgDzy&YN)(eZ;D<5sKHMUj5jar+7AkoNY4Jkkg<3b{{OR)G0K<~G%ci@0vohQzyPIjlBF6%wIFJh+tp+XWShwxi(Ft5xBy86!1cN^lTnErF%=5xh{fxJ>S0Mu2t#*bZLPQ@%J06qq-?AukApD|bq^7Ep&;kU?F6TNS{ziMFr0JwnS1RhEYuhCnwfBTLOz0r&DT<Xm&8S-NR_f+qA-V~D^Xc(UP!d?T!2Q~KB!V6uH{s~v7EXP1Ic4w^>KARiTff7;ZotuK8)h=GlIqmOD#iNv91MirF1gDKJW?Oxpa8yq9IpMk{Xfq24fO}JrRR!LZ5Gtsvu3-3#cxhLTg@y?8C@wzB;`SIZscJErqsjF~)O&o_yigSCtF}&W&g5!bm`c8@Y}}v+K(wRI&Y&ZmeFrp;`uk_^Z^)(ML<>Dln#gGPJJ`B#X-I>qRF@qA>S*$HSiFyFad*?Kh#w`EpZ}qoEnF8JT?QBa3nt3E_&;sUT2+u|CEVk@2=f)JO0wV(yE`7_s`8_BSQ(j(NkW0f<30lxkZgNurWxB$<p@-4=q3jc1s`W3KlO8D*?qpjM*6CxfysYdI?n&<++0>_h56e%efQz-e4ol0gyECrTG=;%xHJC}X4uZ1Ok+$6ymJ$Z7ukdG+oWh8oMO2oxf>=p^EVvD#E9rkl>uK0*vJS*tF|5hfqJ!N&e7rN34(hrxB2XJ|VLS3KpqX&8YlqH%e>Cz*(VBdq6@i<rk%fWj!R?|{6$RHZqB-)Q;;l9D4>om|cnuRw3u)ZTTQKsdxdtXRy8M(4r-Z`_?(L;{Oi!&y*E3G(^<h=|8|WDZ&pfT{ef`x?cyr^9HL(TWpte*>R1f<n4Ok|<%YRK;*2@dX;^m3OM@0a<Dssvx<;s!uE%|BB!uS!yhd>ga;f=(PEj-=o#0GSr$`M$QqI*(N0|axZ4rKy{;9HkBMQ**!Hn9~Kcxxh+SBt4V=bmnB%&efG#(sN!n^KA=fG(1^RO`C-Besq;k5DPgz+Bh|1@YT6;zz@@s|iM8sby3xtlyi&TbW#?v_NZAQ;VAN)ykNFnKF8b?|4)ihWw$x2i*A!lx4e5tNbwkjgt5ank<oNhid;_jyZrXh9Xa-(_Z6B5cY{xb*bnk=uwa1|v#EVcSYaUjKD^RTDD0Mb;iUF%>VMc$Fky0jv=at52RJy}kP{81l62_C6>a6~&8c^?Bls0GdX^ikWTn>FoXg?=%%on~dK>VBiL+aAdS%Q|PFVaRrR>Lmn$_g_<Q1`-<N~72@$^gQ2186!!JiMu_40cPZpkOx=q@-ooo1O!7otb$Tad7}(=YzFlQhlVPX1Q%y83vwVLZgm$Y+sO#NI)1;oQXl$yegB%?~_0WDGug0S&1TP?zMu21y=%B<2M_NRrHS}+<#$Ye#41=MRfNQ<8_!OM<c0yTpY3VWN3mRQa(itn~P*RmK5!S9=uh?jc6?8QfbS%hAKqO)%L2(1h{9*s)&P>5ou+C?F{<;GeUZVGR0Xf7?7Y55N|uHia-O0qS=*W6)ZL>ky-~jb0<X$@~IJy)h1KB6L{geG@*5(*mr$0@O$1OJ6<yIq*8U*)XS~COR6ukFNo`(I|SiS?Q5y?5)V<H+m%kglGZa$q%P2tv9|=*uA*qK8ioES1i+Z6wgA*+D@G(p3-UTSuPQI8DMwPohxd`M4q<lfGJg?96xX&el03x97c5RAUh=>R<;wE1IHdY1UrQFkO)SLgRW=Tbt0eSsXAvMJT9DV#yBPjO1yoQ$v|x1%e8CNGI^0aD6d7uAi^ZuVRFsQ*b`rTuEZT~hg#M)r2o<unu%y6CN2Ov>u7sWthgg%!5m`N8wN@;~<t89z!G|1Ojv+FS5?zsP3R<%I{5W}AL;gs&DC;zvjlC-D`fhcq*x$1ke*m5{OL&qhKQzhTD#<9&H&E#cZI})5N)G}I!7fdB?lolE#F;Hs6qZPN(`xBUlFy|pASP;dw9~mv&}RBr=-tX<&M*SBq^x2!TP_u=c#<yDz;dn_4MnQD5s+-m@zAKohcq;y;mptq8M(^x07M+Y;r)atM-+c0Hz5lxA45ITqoHXEj$E#=g0LkS(44vDAbw7{BaLeSoISb#xIL}@PDAe=4bqiiyROpyI^9WO)qk1~r-UXE+uvS0Y6;C=kXDT&SPO*#Ld&f1f&f~*K@%X;L@iR;UlON=&k0Di86Wn-qnq`Rs5Melo@teG{go(1X0Ce6g6^bP+mu(4w3JxmWI3tH(N!f0#D)fc6w6y=I&lD)h{)~>D}P$aH)fpk1;s!Q<9Qn8F+k!3bj#z+qstTEOU3>DgmjFgLxCL=rzUB}8Gm&Ys&#dam9lm`Y(d1IB56<&QJ*Xb5!b)r{<F@W3QNSya_pxP)>2UcCBLwV6pXHAtO?tQ5;vm7zfAE!sQFIuH;b+1)fLn=YR_dsU@0Aorq4(OcV6kFD&U)0e6h+O=V6CWAqi$RVrUYMz|l78$w~nY+?k8W!NvEplis`T{p6$o&Bk9&3_Aid;UOh7`692Xp==B=Cmb9SZ8c~NleMW_D5-e?qx|mXkA5*+`jw;X)8@<q<f3}z8h4KTx;7a-BIPo5;;5`)lEkf6?$%@<=b1;Nk(lRmwbWZloc<kqWC#OXP%d$72#V)Qq^x;h8-O~b45g!IDzi>V7Hv~P6YE&X`q`mVT%D;VBvrA@7Y#8?1zn@z!loiQt7By=I$Ah0D<1SzxZ;)7=xM^a3gt1@*6VTe3mOA;0R$+N)+DmEL{BjW>xJ}PeMCuyUyfQa*KH>_u$yTDwJns3%%I4Eq6kxP5?E29OnF>KP(%|M%`F=4iJJ_VUeq_1F?d>)2#<+You`i_rX>p3Cd5h=O=bKQMJ1RVyS^lp0?EZV(`?YSq)n`^2woP*ClBGTP?|?lHO#?@+%W`<E}PENOuH&rH<qRS2BiKZ{F61!t7t@_ZJrU5!aFs{nFF-gA~X|7;>tzHwp<uKeM}+QTGPyn4S-g;EF!gXHN`PluW91vlS9!|dp3xh$E(Y68L=c`%Pm6yk4u+vEzvsJ3<WAhqmgtpr)Y&cq4+#&vZ|{!97Bf}sN|hl>R}}eLOvK|=(3CMx)PVNrK;@Ub(3$7U-GMfTV4i10Z_z?>OOgl0LI7lz?9Z_2|b^^jzpO$4Kl!#5WfJ7U<(HSLiVtBq`!9AVcCMgR4(GNmGi8Q5jz1bcy*B}62?kkxZs7W3uRN`Gaa1k>Eyw(t2!r)#<8lStz9bG%1M5PN2?=KpzjD(5vsk_sP@o$V`a%ZuXmb!ZuNw&Qj{M`j*~<xRK>RJTy{Cq890))a^IqfoSLIq!6=_cR_c}DCP?S5YR1?#;VA>}Xu)81g+yySvkWMGN^`r8qTn1E$L3lKrQ}s=pTR(#1;yCEaVekeXGz{=oDaqcC5~zlg;~qz9E)beWQ-WDAk3$)6B+1Tt}lv<LDhSheUjgAUESGV_7k8bHj~Ge6Qq*<&;u!1O%gn5k)h(unpH%E%p;E*R;-jnTQZVHYCLcJfq1%JH7`YlaT#mU3rDT{SSZ0Za=9NSR0`ACXl@Y!(C{4tRw~s}W&sLJHdUZOBih94%fQsdqbpFYklfers)X6_Lsl0S*xr){cIKBO0xN<WXa0lR(zr_JE3Tgevj-`EA*1UAvik_6nyAX9k(okaYL_vVCz9!`H2s&=CE7|rB7iw);*BweyA>Z|?l@CVpdPxf$(|@wFUlO3YcKBZs1$wjooh;8)ImgSZb*7zOfX+#mB-Oaa;E8`?>3vo$;y;;l2m(E$dA?hQnw45G<m>;DmT+2vH(@hq+V1_Ht3PMG<C+$E)ho;%<<A0H5QM{saK#aRtQSUBN7wP@YL+QkBXR;TpYX?xOqU!Lrn$N)8}&MdaUyM*F|}M=Zo1-B376J46X;c*1Zl^E@H4yTE?5{le^XWf+wkxEjIKTmv*TFcSUSxyc`4IIL1miqMo@|&2DF_w|<3;*VC(L_b|H5tuU_lHQi?lCGj$XaRoLug`p^vA{T^+*f}$GWrE%5Bse(La4d*DECVpDXXN#S0k5J^2}tiWODhic*W<q-j4_vI$;8>pc81a{&4z}HJkqL6$3)(i2w_@M{AuZ!a3z{pkI0otd(73Cws=naGgrie;U96&qaK8VkeZi%Rak$HQd_P@WL#y-S3%?cNV`Nx5+__|@=_~kkYpR_c_ej8ZZ0Gu>x_XM(fSgYac>q-zT$NUnZi3Cv7Drhe(-@q-BEYZYf7w%#3Ir4$<Q3S6cNW^Wia2@gVB)T39L4y)MpKuQGq?-q3QKcLkKFhG=_KoA}8GhFAOtYYLzBnWdu;De-@hJS!fF{Vny#rpTP;MlvdW$LSr*LlgfxH{46IrL46X2G<szX($M$3*_^7?HWUhFrY9Xan=}{$rjBsErlE|4cS3unxrOLt4)3cJ@Jz+w7&S!VyC#n0q|TgAwgc!<rT~juBB7DQVKGw$X-H!s^9VscdgvzvSTIgDbU;R)$}nhEe@i-DvALQG(RIP#!migG?lQ@fWDVfU+86ZG!wgqVYl24GOIR5bz`Rx?b0zmv;d2xlUMyU~f?<SMTATl)%_qyWV7CmzJG5;r&!V(_)d*-3PeqLwU5zzJWlNHyjm(`!ElsTAM5F(PY=~4|vqt@^f=b6MFTFm2bwdfrj+%nK4i?S~j!&dco|0OvC71T`%;HR;&JaIPD!p0S5Bh9au1m3{DiLBC!lfnlBvwtmLSA|7RHrBV<Ln~=U0`)kuVO7FljWr5v{WQk^1;t*U<<-!S15=}hW})zM|tc=S5_Pz^4Yurn$#@jZ4+vM>TF(FR#2B>=0evgLD7Ieg!7WqvP-0j(L}?^2cdvxRb-1DCWv2dh-4Kc)`SQoj*(dOJ2yqqE$vl#0g9Q|bg~WMor&V6#4k!|TDU@noQurddqa2UaTs&_#{iWNE(9Q!L&2yC$efbj<7sv|dZLguPqRrVx|%z0vd|$Ie{f;JF47Q<O}S`N-wI5VN2OGvX1EVKxG7w1q07&d6Mm6Op>y}LCKNFbNvO02g1r3wm#jN*y5&GsxfvPxnYF@sybx2_#@Z^B&rngoaXkE5@^QU5i;v`Gg0D7}bw!(J!0Ko~wNQIStx+9Pq+xz8=Uf}_??QnFoloU4s~m@=X>~P8+sU08hwR^?bf>8+l7)B@B*=sll$yB9R4m`Y7bH$JO-~IQaTirnMwX_T19I+W4|_06iUd{~a>I+G!oW*Z_n`ZarM*Q<<Avm(x>=xrGgpu^0x66;RJ{wMJWi>81fv>grEF~%t<J+r<(p8BDb=Fn&T_om>$2sBb2Oh7dTJpQ#>OB6S!X!6A(PyX3V4uan9x?U{dfTdt;&N|C^w_#n7rR5=8ae^QvCz8f-ghV@Q@AA<-we_!cYs;3#&}(7&(rMJcWy8w>Z@^N^u4+T{uC7pEbtmB$A*~Gr52u^QxV*sst8R^mn3~5zrW-ZgECz)y!i!Fw>-Ip0&j&hgQmt?fVjW!JV%>2miOO)`xzbN78?FAwdhj?EELJdp$dURk%`J`#fPcmM)0&g(NgvBni9JsYXJ6i7fmvtxxd}RIU{V*`;vI5wK0*fI6U^iz3mQl>Ula3RH>Q`T|>l)iE@6gj?rd1&kvj3;R;qe%{2nAbTP(_$Gzcssj8JJf|$jUJ|yrXq@D$FH8@2w`_i)#$-s}YkP6!>e7^ipLn(}n?<-E8z_sg><ZaEvAwSlFS1-j6-80F%`GjIX{}0s8?Z74Jip&ZWq2pqc#mA!T-_7RCnxs_g**+$UC3DDRTnH3IR_i`j~-<md3@AmK1+(Y%^YLtrK+$LL-D10i$ycYvZb4sGPA6$LZe$L<ajL!E3QR>QTyySn;K1zWpx(%WaXkYXK!SR%aZI>E*>yUVw|Sk^S@-F8cBZ6&p-_m;HgG<RE^ru$+JKmV0pu==bdPrasHL+a^P<R%5#e&D9>5;-fnXNXl(JSO3zvp=94W+tH{hHuo$Ny&Rt)X8#%e+0|xjyL6lRqH~mW+Lilp2jG#80>vX5Q`B*L<sZN+o<Rn?;!J@xeR*modD?p?x$E#=zJzmH2x?%{7{3=gY7|m;x=0cL4C|KxtMa(YaaciPg5WuF&-9pW?wdTGGLq89Mn#r1?&2|F|a&l#C29^==I3^t?=`Wj}K;^R0ic>NcqYvvDd4Cd8Ft6f7adJD==aVaM#xsZ|k`r~Jy-EUd-f%wG*{sUo=303KmkYhJscX&EiC;qdit_A`FD~T&SrciCk}JB03OgX?%kyhPszFP{jHHT2acwDrvSF*8@pXKyyhJZ%5z<Q8&a#8SdX`b5U~o><Y+H7ucu5;-dZ&78rY4CN6lEZhz@M@=T#LTYP%dR+dZHUj*^CxFsH!qL1Chi_1B3#^-!aSb5a>=rIDmcnJILdVM9EV1Ir)8^NQz@A95nDPKm&^g*==i8Q{9c%y8uH%lmje**xR{rt0mWlN`(S2k{dtb(v=rQ=#t@0^NYrbd>Q|$P&d7vYwQ$0O9-RUR3>Z(lI0g#RjQ=6rq?xXer&2DE5$##iD*tpr7u$rR?;iU#5Z~N3d?hI;HP+1&5T7I%mi|TW2LxXNa1%MPjuoSprRKPc!;--Gh}uzBT>?Fbc{=(P2-%`mF*ii7Bz*$BnnHU(i!YXla^K1Vq2eNtNdX6%M2D-c`w+klU-c;hfu4gu_`~ZU1}cz+VFCw_`L_>4x(d3-AG4iSca#f?`4F~Se=ZBNHOef%myQYBLDq_X66*^V*OU^bSIm1trXfJ?oZ4TcFYgQ5M>~oKsIB}7$qOJ81P;#ukN{xE+#;VqN99$dZzO_g((1?z1sZ07-Pi=fHZmSyZgJ3#{H!A)x6OOM-RZDv%tl<Z8J5!;Em4oR}aW*zG0H}1^&-nlI1(gWl#<VxP2zSu6!lv3az&jmpfLv$%xKAQ;gDKgFR)MX0NcTH1VveulpTb?rG%%3;meJDG0PI6#j0VasJe1($YCTayI`1P`HkW')).decode('utf-8'))
_LEGACY_ACTIONS_6C8S_3Q = json.loads(zlib.decompress(base64.b85decode('c-rk<%Whm*a{L#rxlld$kaujU#uA3z6ewwkaf4_y;4uss<3-y$!~brXDpuXPCo(c3&nc1`a91jp?mh3585tS*>;Ihm+wXt;{cnGq{L`-|KYjgp{r<O4SD(Lpz1^JLpPu~t@BjI)|Ml%J-#-5R_dovQZ~y)6^RFi#K0f?a`|#7(zy5ah%g3Luu1`)+-rd}toGzQMKY!S4K284cd9!){?d!V_o2xG;rx&xYf8Jc*{Bm--*!}#|?alkI@4oE+$NByJ|DH}e_UYrhKY#tSf74>pw_i{0HlM#dwDp&p+b<s;KJC7meK;J5&ztM({aaV_w>~~@@+#1f>1+3&=2L+hFne7%d$5PQmORYK;-IhFUy*lxy1sh1iN+K4=kY&)x6Rs3-n#uS)A4ND@$lU*`^9k3*X>LNKTAh=b2WeeetBGd+1$<-(fqr^)dQFAa=wT@-+Y}fqIPlq>Hl}e!8fzsv8ika=Wu{$qqOheyQ}TeeEiY(ojK{cHJAJ0YG3*|3e#Vu(*^b)njEkbniWjmvK@OcW|QG)W~}{<K4aT)r$cw}-1*Mi4`Dk^!Ma=sha1=o;nB*^mV+*6Ba055eDWS!s*k1oO+Jrc2)8E;n4@go^g-OcWB1|P+4~uN@CI%_?mZ9Q{*q4m*yqy;AJT!x|2uip(C4Nfp5d{xTV)kklgVLfTp(kfIzL;T?fc{{nA;=dr;QmgrUmbAuCF)mzWny5&Fz<u*B}4o@Jtvqc;%NEOQigcBhA6%tvzW^xQBL*$n3|#RepAFSb#5j{TuT;@8i1e-KO?mr%eLPyT*K+7~x>yR{RWLjKDpCd$nEKmYK}^Fzs#D$8-RJV{aIw%vFJ(vInxUK%deFGLJyCA3OZfxXDEaDjrnH_Ek0z_09A7C!S89>#G1y>EoccY&Z|VxZgjrH3sv|-vTGZw#?gSJuWp>32yephV|>y#y?HI_kj(yRzdE%VG!F2?csa~qc3K#__tH<_68v}(s9VHTIrCi*blq6P7W;p?iAbJ(>ZGh5whNOC(!$~%h;e7ZDm-v9TP&4j?<L2-!Pk~<v~n_f;~nT{T}s8u~C9vC4-SehR(q|hqC^0fUDQXzCQK`e5?*&jWBiM$U6+-r;yW`4WI-e`S#t72g}?!4PPmGjRv057l6zxq6!G&p;Au!NmRYpk!2TrFg72qZvPT>Y}}1+pao(S8x7U2FU296jztf}pdFkx2Du{>bO9-R(03jC{#I|$kx{i9l<7$2a0tLx4wl`1jXn;_KH@14`u>UNs+qoTVxa37%$%b^?=$d*N`$$6a7&YVH5*<Z+Y1t%WtP+Scb5;_y)~xJF!6EWm{waO=JS`^tGk~zx3_-<mP`p@N;?$39nvtD!{H{@z@QO}`y-%HPY6O;cc)=S&Y`I4T^b_`Rp9AZCf3wCnPN>I!o)$9uJy6|u)EUp$7wj*<BdGow3z%lFx1)Qoy<p|xC)|vTVH=~X4N7@pT0M=5@Ky{IYM|7xZ2L+Dlp;E=y<Pzt>+4pojcgkS*KmIx-T4`LcA=o5s0CJj#tH*roMUx##F8qhE_~2!MmHA>xZ-$Xj*OmxSgPH=i~d6vaPrG=W%b1ucf0?GY1((Vi0F#KGe~zARD}gvtqC1-9(6>9E>Gj2<#t_sWjS9C`}RbL$vsqdS6R0R2Mx=_g(tfQEl`yMam@fw)s@XJ2z2&gx5p>o6f_rUK0_@IN?kkCKhz>0;BWobfcqhep*zv0UKuYNgot&>a+mzJawkV_yRu3%)C986?JZA%PvY0yTjPnI=8%F#;R?OiIgeL(UrqnGhT%Uh@k9UkZl^Y0bIZAI@8e##h=awDEPX)$%7wqNFg{cR?cL@jNLpv+p`d)dz)tD#Z)f^QeXhtF0y2xePI5tl8kCb9Nz_>NJev#U)p0mupLAbO!a(nmcweVK=>az4d9SnewxH1TU0Q=Wr+{L_FKDNM%iX<$a%i9;D>yqnLV-V1uy_YTf-XXw#)3fVgEdnhl1RsgH7NWWZ_npw(?3g8VJTMo^whIz?c`#HfNjz*cuFf<&Xsfs&hU4;b$rRkB?MZQo*Y!k3dfNeuiA|F-Y#h_CfktfN!z4VF~0+35Bgq0DoqA9)<J`aJ%*yY=d(Bc30LE4USBIVAK(3j>;ctLLr=(%I#OoQmW>87_I@hE_W0BXz>30@%qo(l^6L*?Jx68zaEf$yQROsZy`bl60$yx*R0(s28+&y6*zd?<Me@-?N%b#@`AXHm7imVp@h`aW6Dv1BYSVAPmSRQC~2*E4vkb2dWZ`%JxX%YshAsOjpZr_Ok1}NNnnX<5g(p?&Ka2N7By<maU>1Y%CEIXX))&7(q`Eu!}m&Tq30A_4`&AN)V>P;R&!1y$G7mInsA=EMxk#us&!-=(Ao1mTD?7N#e)m0b*#n?51bYXt)vr4oWjA&tbIWX>C9bm&r|Mj7B%3>cOUz7*!CwjIm~-n)yo@$Nd4&cNU3K10l|Qu4W)C-uCCyRucI@C{7%!TI);M|43Eq|Cj?zDwyC@8sl&?b7%@jO&z8(>ewayw?M&I1wUP&W(lD7P->zcluw<OJy8=W}&|3b^2wUT|1X2qnsE2wGy*R|K#dRjt^oltg1qJY-{;(F=ZSe`(RmWYHQ%2DC*VI9b2oYeNHQq632y#mkfsxkst+4r$7fbPb65u479CbnzIC%h4f(94t&R7$hKeyMH)`k`;ZMSxEfp{j+#aRX_Or5c!GLEPUNLL|V1LRi}!eNR9T@X=w3co{{%p-m1oW>_;RsH0734;hsv6s-S*TH(-p2xu`WbeQ11A~evFD8KAwv7hRh2XX4^P+C(Hm?#(ms`mqB9&0m#eJXTaWP8^nExu<p$4y)Tv3lJPW`9~vklN7Y4nK)?$AR9%3<SInbce42Na@qtz*n!Z`xW0PSqxpJGaxfh+)@bByADDHfwdXFjEZot>N`1*{Y1@i^MX?Y6}2$eZI9Yak72zP{T|^(A>qFdjkYvTy3&00K%~U3WnctTQA#SMO=YGNh_rRa!3$k0L4a8nvi=YEF^GrZQ{mA^TM#adehrAg@W5LJO*;C9$9bGI*sF2*TG|x&b4RJGzLvtNpn~UbC1NLX$RWgVsfR>Lw0fjKY$Jc7aHvD<KgTH$%xV%fFHH->CASA;{uYG<sLg5Pq%7mWPo&kZjok@Z9!2%<I-`|o{_?6u^Fk&jEx^&5a}LaZH`l|^EK4hp)S-|t@5EY(&a#)oit%k)5^g+@ses{^nv1CIbnf=FwdL3(DF5PZ#nhHL(g##Wdep}IhUM<QL}CoG6{mK`_fSjLD4(NWF9_Gy)roaED2b18GTu){&jG+>epqs_G|ezjBk_;Jj*dG72}|VGTJ6n)FdC#*vOc%B`d@O;DPKqkd3QGnP!)EPX<;r2pfSB-@hWlqvy0}(*aYCry+oDA^$xUt?XJglmtQ3W?tfwVb(F-#34{7mrhtX-X@Vf;-;~&EON2aI5$J;paw+oMVnz(kQu`kSENjqkdK-Boc2IbSP34&rLd}Q1aX&HtBD3#j*O7rS@EpaHP)7Iw5C|+^1Ldm>CTeTno0{Z*z3e0-Eq}74e4V;Zr@>KrKC@%&6WFSXj)UzJL5z&5!ITAAcYRyMuFO==x^2Y;wi~1PT4jax7lMf{n8R6ftTHv)An2@IL+~a7{GE+1Ee7mTr)xSjFdVnMg(6Jg^4$2f=Yn^L!2@Y-?!uj+W9Zii~1Fodqtes0@9HX5C-LBojhJx)Rkn)5^9}IIj($fBq}Kt*3+zvatalj_%!i`(I-+bua9YOm0QlWA9ORCY<h8I*yd<C51m;(jL6mF^a}Z(2Em0%2v3|H(icb;>GFv%{Ui=qp1Or#;<VWkS~Jx!5(2Gk$Q5@)Tn1}H&7M-KPNTU2yKas#3kP-;MI{Ill6NV&eiTkj`*wL>I>9*Jl`WZ2-cxAqX)j4Z^^j4|!lYZDfyfF|s2G;cgekPIRm{++QNU-GV<RZ<Nog#wpgO#MaAwRqHKd6|>jbr))zs`BLEGp5p7wl+nHreWibXAc2xQ>NI2!HI2szYJUO^0J6aa!&T%gK8aCISib==j23uLp&)QeiY5?rlCY#?>VDwENPDFGXW`>E_|GY6e1?9t$QI$~<ddqvDkma1vV9EAEFhlp$LBQVK9>Qia>a&{_^94^!xS1RG;kwdw*m*H5d(h8dLr$j!b;1qEsff+9$8*VkO+>!#<m6oi=qTYQq<0YQ9maSEi{insWIK0S+3ydezCBYllkjPd$A;%a^(~6IwqX8K0{IswM9t*`eqb@me%9;<%4JpX-iN2xJo*tDz?);4*%NGj*yoBKab8gjT$lLy;)e>e7@o`Jye)oLeP95BR4bPVq5$CB0vXL;>*Tv8+kc@Af^{%R*%xVy#;3Is)J1=<MUkRa$*<bWc_3{ke`UV8IpazaUS~4|(vhs_ee0?OlXw;f)<RizrMfrB$SaI>Q`=0y@%~mayCDTmQTtlNa8H!S2uo@2Mp%O@MeSXn%HW>0=RW#VAvM;H;TP*<6Q|1{MU0@SZ`f_D@84$_+)ixMgW4i)m@NkA{aD7OXNxFw)VuYtQPvjFQ_rfZOL9GckiGu!0HUCT$>;NsO^;k-RXF>QlA0RLL!Q+rxc6_|sGnimCD5!TX2ldu%Oz-UZe4Dt4aOm7T5xW=0@YqS8c|3!XsuBH{D9@Xf<8og^rSC#^bo!;mX*Oz!)QP>V*(%VgVLvN6e!d0n5r09f_!tghsvTWa)N(}SH&C1Y+=woE;!Ye-x(H>1F7GQ9jljXBPw8~IrkVPV-z`lm(=msUyIAQy;YHTPxmJdV7*h(%Hb<mQ=xP=edZf{LsrZ@bYegn|Nh8h5DP$B>8qeh<h$K3Mdt!u0-C}e2z8x_E7xzY7oO;L-$vWwX%mxPQW>LyTRTE3-?jS_?9<{)=wWKuLEaBsGbYr8gDUBf99=Td!9Ofqq9WZ)wiF_+P^93|C;l*c@GO{NtLxF^>a7HfCQshYqt5U}<O42HD4&HzKXOeOJUEXA(S$3|U3x)1AZ<=@eRLaq32o<X-D0~y-hon-~z4Luql^5AJWH-~|g`gxqm1UicUakyTLW@iw1^rn@`|$ZIasm!t`QXGY)`1td1iH41x4|A<zElc9jVV8jG{8#|c9k6~&;>GhLl^X`5Mj&Yf{H9;MVX_QSRiK-6hX2vbOYqtiG}~VgD%x<0YRF-ms*h4Y@l@JaZ`s_52EH>)5K0*fdBw|;rDTK#3E*BXi^GDrC4sj{+&uRpUWA|Oo8~koM$bBs}tV0aYvEY<2VRiGf@P-vX(SeGLAb{^cN(pxX@l8;s3l^rM*;QZ8)^ah<5~jG?_tb-dK)?E68BSua_k?0Ln~Ci1?d93i$km{5!=_GguEK8v-7cq$Eiq$u~bTodkCsrpP1?H%vmKPx`iyLOxK=aDWQiq+<3Qul|7u=+BsD9n&zl^>q}E#(}d)D!f-}(f6D^Qp$C7=O%GUhDkqJ$~6e`4;RTR=$<_`XLM$ERdrv0;49S<SSEKxgv_WOkjOKt@wMf>k@*dF6FizgV5a2NYoPG@exNcOQqjqf5uMbaO9>6i8^4o$bAi`AIATtHDm6njr`yX><_jZ8&KzWF#wNkeIFOsd0jNu7PL!N-?DOzcv<ZCGwYJ#=NT8cF6`#pGHKP*Xxue*xrqORC$p=x1x=t4XYy_H4qzNL57@3wPCGUx)K~eyHgKJy^)4<WEQjr#Az%N409%H&hpe50eY&%G6TojL7F}_TAkA^`NpCRHts%axk2RgdY$ULQ$3o#dC|C5KcFqChhuGfTMPmy7CYVg`EJY=J+-t2H`<MOkmDt9x;G*`e?CB`?7sg|r~o>nDAtpYPE)=Mxhy3-?JUE4~LfL`&Y$zD3BCpq0%mn^O6ABSA=%+d@`29WiuH_)gUZ@xy!7+<fTmgIydvjF}*uQo()9Zz2lP05I&r>|Up!mr6VLT=m88WA}x2HA+wDaNVQX<}xFb|Tv^X=%nHB&gNc5S8N;Ewx&tSTFZMb^j7)s7vUFqIP`TAdf|)O8KjRRRTc<oLV&~8QhsqR6H6P_LWmEc)69$XQNhuKkgoZ#gz=#em^pml?A!-7`hmiXVjUr7jMge3sIzYU~4cbx${>Bl9mSIY8S4gIXWsMA(U(%U2a6%Sz4J4iI*`rIh@B!Qj*jplDy_@o1_OVxkK1rt9<G-5*m?xr1F|Q^K@o_KYV38Q}fG!k0j1HqA%jzuXaVr2hwH*X)lmLsV}LTWX=J^)Dp3#pwmULW6xd`O>4irUIq@8Xz3_KEvG=naGq9%Zs@ricOnRPcGSWdj#f=>sB}`f4&yr<hw{20YW)|h{kCf-f?8yjmX4>Xr)ED(ODh2o%ZWNF{Z(!JB7E5rR+N({@qo)KOsUz?5<4_}Mi2|}{ceSFrJ|qV2q&yLOJPysTQOFHaSw2vkd5eO7XZ=}A>v~X#<&n3eRJPe_Cti~D3hu(;urT$VF{72q*XJCsek@Dam$D3IoN8I4Aq2Jn%*9Iu1-)!y|XoU)@7=O1@ctnPjp63YE>FKK*^Q_>-|X5M;(4Tvs6fH`MmH%Tff3nhYAK0vmw(=7plOYG8u};7O^3)Q(J!o$O*T<A<G63a^y&XqHxF1CXpW$XB_6Vq6(`KcB>nZ0-7`QE9%QcVl^W>H!5TB0J}Oc*Wb`w!iY)r{KZ{ge2!rP-K-1B%11-4(mOiM7XuwAh%7S$$W&1_T*|=}YrMonSE$uOeU4fAwO#S0{5utN8(SV0m4eNxR7h7jDr`|isYFQ+Fzpz7>enM8*b`U;0nO_0U+JV1<Fi{IsC5~u$y$`qQYuVI2_-Fz6D(EaA&RV;+=gr~Kco}ijz?PjC5AiPIs=qe*MfP6En{f`c#A3UqLj^m(=^FB%a)|Tv+yQ9$(e3Z=Nwv;a#d}84NpXc^Hq(`l!Tt(`mI-r7DdFmHIKm2g^9Epn7RKdJtdM1Q)PG)xGIb0lo)8tvkzTbLW0Rk85!6iDpHec!fB;MGYMsO%4pTBxI|VaN*1VT=^fIzSRledD%6}7l!_?Xj08A#?sE#KNMHyneZ~kvaCZq&$9#z$pZ0^Y<DRh&@Q+_BYl0vr7|L@O%TihT&s{Go^~}X+(Glup)j=I<d3987RuaKT*wILpA0i}GP|mE#EE$qYd5w%(fzQ_SoZRDc*SNc9!ot+FI9UQ%P}DBw_E3x1&03%5a_3pDimqs2!sp7XfkgnuNTV?)mI2EqOT=Tdj4eY4Pne&xAw}RwAqmkI%{h8v7ELlSBr_<R7w*GFpF0x$&V~Lk+6oqFZo^C1D;BfA<#d@PadGm+N4+_`QCcKfT%B63>(Jsp%;jwDfjG;UpVx&Xr*mi4-j;M$sLRR169-g&zz12!ySj@#(7dAui7;fvDOr+@UEk`}XawLO(n>Z`+YYbo5Jn%fKNW0@vlWflNpSqy$yM6PLrTmWi5GGX^O!n`19)ayS0q*Q!6mZvKENd>bu5iWJ<87Y%~CHqHa%BYXRSulIoD`PO{XKnW^06tttqo;Js>SEx{MbK!@+_L16bMg&uJ#zS>E@t+@v14Zn(`@JlX)@?&2si(IqenGi8ZjQpGC^wxW?j1z=OeJWFCiwK^}LKr@Md7lB8Of3170P{JbSgHd(fjU>0Gnf=Tuy^DkUMUs(XN*2oyab5xAO2Bvon*Sp#VbsE0UOhQlnB`ZZBe7L%o(^G9cGHvGsn@~a`lbwDO}GIbiAF4krI*Xo>TwZY+RzcsJUzYepQaQgf!4Mh&kT|fYM8m2<DQ2&wS9|fT$08#o;`)*5^EGmuyvo3u~o+^1w|SEOIURmwdM8g_`JRGLkC*I)uUr5P>e2^EN-VrIt3Y&GT%}~yyj1np%ulrmpOW|eW<urvrJ=J1e^&{5LV}7w+DB(DlK(4FKy3wX_AhfL>KMD#<R($X`o>JnIznu3i|_0vPv8qTL1|_F{`0f?m_0<Zl%*2lbcu{D*BN3cGbPi7em3Z#RW~V3nyfG7M#(m*Q~o3=+P9Th$2Ad;*Czi<EH$boPl>odwuTJnQx^zq+~t4f>$-;uo<m^vQi!%S7XvWL%DiG!&^__OSmk81*+6~G71*5@MXgAsFC#7JzOb({!n`d=h@^_(^o{S#+_n#B`<j;&5=xgjPFjBA+cDMf|fFQEYCFoLuiy!Q|6DX%?$2IZZ4LnGfvb*Uyc-%X(Z~V7Thw6DO0kdXR)^LEiYE0Kb@s$ade2HF2|Wy(ic`FP7~G2<RFcyyew@wu(m|~FxL4_;it-G!@{ixirANoQ6o}Q36xNst4Z6+oK(^*S{O9&UI-!$R_sy9I%NC7Fd2x7vl5~FkDJk&SIa(y^mdUpXa|pXDjIFaI%+8NNU%Dg7$T3v9u8KDnuO&6JEoaR{wrc`VnirYD;=SRrS4p4F2nUOiymYuHPmhw>Wm(BLrWrdk|JBI%@);vsFzZ_cnUajX%O?43kqGnbQQ24q?F=$y_DjMt)N)K7}fYM;7A?0aAIfbYdYq#w%5qYi=COT(ut~9K&0&Rk%_F-*%D<_%;97;-*l`$?PHv2q={WSa$lIkl{lY@M9v5hypqGg6$e8JlG@3@wPN7d1<g(}k}R1SGT|yBBq|X(K>L}Ku1npUlzA8g3Z%rsG=;jo?^vY)t>7EA)dOfnM@ZHsID{_ppiNu@9amXPT__#4VhN1<Pa1ni-i%QmNH-#*5cvq7iqC+FBcAsyAvzy9ZBB?lr6f7U$Bq}2S8kKwFQBYo1eO*`2`)O5*E#mlP{F8%U9>c%U~Ga5D5@1fREQvUiS&t-R>?aeEIEy8h8n0)G8x$;pPuuftWxo$Vl+yLL&qDxdK!JPX(P(e1;DpoWR*a#w0oKKCAwS!;G(2^1<F1$pG%S!t0aDDd4eK|Cb@Q>E+w$e=(>|-#@xuNo<A<rw-V}O2bVA>v_|KX==QL6m*GVsIljQ0ViUJ?%CU=^L@LHPKeAXOSNBF5U#^hAxG>p3i`A`zc7vcL*Ic34o^GgRf}^R2e_2^3$TlMhFq13;A)#)ZpHGe|OQ8|m<5IrRq~Gc}1?W?2c1)?sAR7g>!TOWxp`IlYIoi1Ep2Qc@SFY7GO?1;Tc{*y9dqlZ6C4O#&CG8X|m9u%?bj+v3)(zli;eI1HY>jLj&f(I^PoSJDFaj;oN67re)H8?u9zeQ5j5#c_EP;MLfAdY3Rv`642=Y5QVEDDpA18Kl-NC?#(LuH0Oq3wv!E%#}u!zN@gf7@X!-@ic8VIi*Cq;p^ECNIW*9<m`J0&5|6~R|3%P0|}-I6Bu!9JSk1o%uX@cp=?qq?vI)V$t2bJpdor+pctRwkywd%El>f!JI5ut*28>mUla++|;?Ws02`KM-po@&LwhvM_rYQevG&3#jPGzSOK}<w&mSg|{b^W`OD#X)e2;^KVlZ|FSQ`&Da_!p{2EgWuQu6k}P|0CL*Uz(K0I2P=J;$O7Z_zZ4TrRWi{lb)Ejo7MJYimV}(gX09YaCph{*#!;)zA73Uwh@JRDbtlWo;6CqAd52FOBFzS;q5@tT0=7~vpr+lzw=}#oiLf8O#eKd@K2t`P|M)tg#)us<)M0TA+rnQE4k037=97%Y23xO1sItFR>X11XaZWJ>&<*4I=!1=z`IJ@UWz?#xe3=k&EWol81BqWe;9x+v~61`J$DK+(a7T`^Y-Ij+!iy>&VD$W^~s#<6k{YqW&L~v9y_Lzqf<9G!+<#G_}bFQn)FU~MP^uyF?j9|7GTfec8%%+fIv@(rGwWo@zR6_Kq*EN)HRZi(YxJ8$eHJ~W1C$$!HvFag|FkqMYAdJQ>)oO{1E1#E1dZ?CiUuGTH{)q#Yls*C7a*;SY%e{p|QY2Sn?n{g_O9l;GCG3>L1uz)MCRVB#VTCBRAd??zyPE)PrpL6hOhHw^Ll8em)wB4CZidm=VM7rex!M<=jacd97{VPH5jGdhX1l(V*Q+@ccZxW<x(v;1(2D_{1zrYaC2WgEdLgE1(76%IXcEYYqBo;h;$ZtWIaX|h+1+Lyp&hc(vpQzENOrg-R8k`7<&n08CLWX(_n<88S}tr^*PUSn<RoMA@458Qh|7Z(^rW~G7w3;VuN3GrJ3+P&5g)tLYP1leWW@Fu!QwgKb+>}*i%2USkrNkhyP%TxIM!<m@)CYeuUF&{l$oKP!zK`B@I7@_;9FD!65RE*6aCTZ^>qk|$EbZx{Jd1CPcX1c?Ib~IDhk0C0+AyYCf}l#vw*K$buoqVaxax_ZF-?;NrRnIQO+@wQE0OEXd;iadY3HZSgKT~8-hYzC?YEEm7~)mSZWfZMzV2Y)S6Bsoo+WnrBJ<^a~Z@Xr3>~LPDu*g$R)>|R2XZDnaXbF?{x|1SIQlMx<?R6BENU)0*XYAxPsCF5hMOtd=Of#+dfZgn(_gRXl+i1w`{Kd%4J}mtXWnKt=Crdw`vZX(7?|{;ND(RJ(!SO%hOz3=P{9DCE9<c_v$DBNdQMFsGnAI%uBW8o{4EDZbU>GfP^F!Q0HD#QGWK)zV0S`HB$B?x5jB5M=>Tw4Y-~qmODujBi0fm-A4;<Z$2riC81U3QRtUWR4FL{YNlBz)55EdaBU>lnU@Sq3RnY)`hqqsFtY^24_HB7UuiW^nm%iJyxaB7Uregc+*xI-LK(NUBdVwtR*#3!I{1kY5E&2Sm1FyAKve9Kd%C`g!I<HF-5u@w(#((FC?8l5D_rM?k{4Ukw6q+U_t$>--s+5Rb^m|=P4oZ')).decode('utf-8'))
_LEGACY_ACTIONS_6C12S_4Q_FIRST_YARN = json.loads(zlib.decompress(base64.b85decode('c-rk<%Wfn|a{L#bd0;(QBz5C-*J>Ke88%3^3ade3Fo0GNAgm4}-Gu#j^^*0-%CImu^N3`#N4yn^#msnzyScgfFaLY?@4x;2x4-^=_D{c@{qW_}-N#=)-#$Kld03xq&(HqjxBvRL|Ni=yuOI*R+wcGR*Z=wY`IoaFKRy3d`|!h;zx;ap^QWI~@6OK8KHP84&gaF~k3X*0p9g<<T(3WV{d)7``u6GU{A%>|PwTt;pU=)`ho66bxc~U&!_)CUR@?30&xalR{OQA=zkEKvX*THFFK3(e<I{6nf4+Zs`tkYG;j7Vy(}8$g-`ySGx){H8|G2@cKtqPFJ$@Qb1!}<Pb=BE}Jv_AJc}`|0eck<vyzBGb?T2-3JW+r4{{Y@LYBzc7?q7!ES+wK%yPuDX;iRv-nX3FO9O3ot`2EM_ar?A>7%!sncc-fdF5UTf5k202884!8asKHaJLBY=QSaDPmV<LTz@t$*_V2^(ZfWj+^s+MtUAN})I9%mR_oFcURXAN>|DnkNJE2&?<So0g2V*uEj$+2j-{>>88+ST%C(j-4yyFm-(^OfPGvROpo1uEN^0Vcn3);w{LnofReM|MRl)s7R5e(t(gaLCD&6_@mhj$!4d_8*~(Fbqfj^p0);N36jr1yP3o$xLl*#Ga~O<kWGe)tBD9o;I6iZvM=rp5)*=c(hf)!DwU-h#0`LVjA95q(<l;r{M!{o(1?Kdm30KHYu#*V8kh)8M6FVl0vLJ0_Zg{jEJ{PjwF+9FftFD_8mD*02EI^!hjEcihKi-n$L$zebw`n0JNwI55J&!p-;@z!-sh0{3dSv@J84_hH!EsE^?Q0>|DkNSUhwKSd8@V}U+}4`d#JXg@aiqxB{y9jN-CO17`Efv9gD&p+{W+FV}+cnTi}y=B9B0LK0Ck)<&hZ~hWEA+}}QKI?IzsY-COS2nEQpVt3r^1Tmis3iulXH7-{0+K~jgI#QGR~$ogDz|fJ9VD*7$Pj3R>ZFUIi-CY}#_FY!yc-#~emt(*Mg_dgc{DW^z*}nbAKnO>4UsZW$nbEhEq*iwr~#a20e}SOq9fAffQGBI>&ZXH(*8Ke+52PPA8TS#b?e2B)q`MqB`P0ST9=tKGvkY!;7HQtGr*9x=wW1cWegM#QgYf)LgKAnD7(`uWAo$f!@txz)(RL6x}&@LVh9=y)uAuRAsUWF3qPP7oHBrTU;;FuAbijd9ea7J>C6Co<S;11k&3Yl0FIn2yW<+&56UrIDG&PbiRe-pzHe+_S<&G=!Ghjg;0>AZaQWbp<MeJIyg#-T;kk5dq|4_$e?sHC)<K`D5w$aw9-kg=H$SW&9{vJ=bSZAcF0pFEmA6|^NE~B2ZAq8l(ndd$eIrVbpM~RQ7=~l`svS}?q8Kdbw3*6i8rmB}h|0r^crdGJeH=a<F6sDj8VtL?V+Y$1b5T1+9-I7)@dzYWL9O4`*DuY?+IZ;GOG7ge&+^_P{4;?%?L01n^G(K%dyg}HtEkn=wrLtHmBlu3d{WHd<W*lc;=}!uXOf`vRq>Ch`yJscnR|r+5QAHAbANyLoTdVesNElTGxYU<{3t{MkG{ASu1nL0&f%mMnKz7_(1|TF9@N?eARDp!$&rUV2b}>!2W0*9zU6zzz)0dt=CYMgp{4+;?s&8@jmo%h2wX{EYVj!zKduvDMbJcmVje$bz&Zr_4fsdEVr<?D#t4*ij!v}k*^t=_Y^>2Ib7a8zQzE<L*mI6Y1zd}fl{%F%w94e5+Cej5MJ;jIY#AF@Fh|t3xTc{LMK;rMxfGP0LvOsp0A+Z(k+B@FvYZ(Z0t(H^%GZ&(#$f{W1OeW8oc4R3&WM)NbxAH_L{Ayzyn2=*$^)kBou~E6n8GZcm_sxQwx={ERM^qF%a3t9i#=spr{#OgV?&&awotoeZsXRmdtNsdtJiI%A;zr?Heq=Lkb57rX!N&ahAXoP!Vf725%jm(sbq)A9A~=e8+By5hlifj7;afA!y%cN^x=tyS)+3}cInQG7p*r4N96=10*c3{7Cra2h8%&#>C2g5iS<s<icmkGA<mr4Z&5QS>n=(=Pw$2}BQr;uX2|<1Zz%XP%L7RyPf+9N@W&R4UXDd~*vCWMx8?}!e=CGtEi;?bM6ubhe>i3mrGn-jq6iMf!#wWq>z_W|{du>*YF<+L%Q%&;1q|P9-<S8z=JBpvkX?C&A%Y_Q5=}5zSvH2iJsy2t2|pLCL$I#}?HF%&cu^%GvvW$dCvYwwxtl|)r@%x?il^tV<;L<blf#1~riGpdIle+P5$v?k%`C|o1C6l23Z<>Y$7ma_4(1&gq-=Kqg|qSj$uMe3ZUrud2&2?pf|w}lfzGAP%)C9vIn2QwV9dZgCO%}7yBnOcE{!AGpiTu(;ucDK;4q+VQ2LP*jG#BG<uP1ok~E$%V$hhdFSR0aioru%h(KYkN6j!4zbsx5a@#C_UHM={=6ZYD-;6W0Qh4CG5TWmRFKhQX`JJW*HHAwKERe_}C+u4<s;N8Zah$F&XsG?{LJ6t^026<(p((qyR<2)5)+BT4%T>(17d^(S6MA%A;};It60aq26#`F(NDj3{j|pjQS;Zj)qSf%mJRO8IyHJT;VJ+Sgx1ilN+~|^xiM6;zr&;+2kDpc^S>oGxh6pf?8h{Fo1x1k?$*s*~JDa{V!$*<q3E0PEB_-Wz0K6CWSw#wF3~Uesy8&G(7cO&QB`cNLt1RM;K-8H*-(|w%MtrEzex-0#&ZJK^Od3y?dY)-OFE>DmH@-%*@+8l0j$F$y0#j~k-!8XF-a@P1=wLO5`@i7^eaq-U+J}y*Io~eiPKYry_sVkAMB1JVL0Hjuxs}Wa%*3Uxwr%pnN!JTlW0O!u!8&OZjP$(8HUcQ%yRwB4ME=l2I!agLS24J%nuF9_N2kPVGzu$CnJdAqevUKNMH1t-QzV5+p<LYR+QJMm;G3<!or6qPw#HB-n5?!6Ag|B27H@_f0u2P)ENt!U!of$#!NQgW$UZrK1;hBbt=DC&qh2iHYHLt>DMrFqFzc=w;y^uH8Mp<R7dCldUN~BjZ8}LBLE?04A(nd}&<$%U+RN+Yzq7p~*(kh~G)LBtK$XGlxKD9O%9+q#c8&qBKpPa4LQA@snaay;CUcHrtclb^I39qyEq8U*n6y=biO5!iU~;wOV$1_svt3lBgP~PoC&t0SuG}h+`6@{7089+E7%m2d{s&7=uH&PjH~|9qv=?<kL(i)-6OF&isn`$0#qe-ElCx>m-xr~iPU+Y4MK<MugEBf6b2=jPspuDR$zaR%o}7qrWcgEy`V{y_OXf1DdTYU9ED|c`f)7V3qfR8VESeKQyyuqo=&+}HeQ0IbsY2uovIx782vO4o#wiGtMH~wf2K>m%6@I<VphO|E=O&+q<nks82Jo*KKU<}{tQ({zOUh9xjYA3l64sDhD=}7pspiF=f87NkS!|5lR#!d>)=6Dd-aAiNj&UgdZmV-roF^i{H|sYIocnSM_zFq1JUj7~IxtY=qygqW(}c%z8;P#K%z$Tt(O(OIS$zg3x~()Av!$gP6EwV?v}32K4UtBYbW>54gD6?UTrKRzOAEzmWi)AP^d(`OP5rK`k%U6L$rufe-(l6utRdGb3x3ojBq~HO>3|6a-%KLv^g$4dw(*>2?B=qHkWPT<^n`6(fQKdfPX*urBqs<}7Fg79POh7!T@S~$o;;H$;4rW|ZamDEsY%5NNDFn_qE7m!M4fbX%%D0<Mpwk8^huiNGZeBgWLcv5=~Me#Pfyc$D<~|WS)m%8ie#pNQd|j=S4BqNNLMI#81=?ELnMLNl&FY^1~3W0lCh9OYDgqrVw=?hiQyE^T_qU}B=YjMy7<mgN)LnD6q1KXO>$ggUhEJ36`^5@nom-Nk2z4>|Dj^I3HlzGP|eR{@*a|8d=kBp_-9gFSrhimx_#iVRp+=IP?fEj_ECvFs6_24Ju9A-4z)Hpslr{X+A>%=^h0;clR>VdA^s^UEd~ah41T2mMPznto&>AYMInBwGN$s`qUJ7|X&o<V*4Gsn;Ibfl%)Xg+Mh`6D)zmCYt69YW1`8Y62JtF!X&a@b-%JJo)?)!=h<X5-A~G<0D3o+#>;W^^!^4Ey%Q`7DkwFm%Xtr!xVP;_hX>$lVIq|*3R+A(RNkemu<}+HEK_o-WTMC&kjnte7m(jHPz~!GTa#m(_kOEERI+k)91QxrW)+4PB>d$i{cJHH(QedKZkBCtyB2Fylf`Uu+TosD_8}uz8gGC3ORQB@H^jM=nReC<fY6U$nHI7!aS_=pbn@4iU<!Y|k)28A%#)uI;Wj=w}B^`cCae+)#11))txRaW{$D~)aBZg>S@mw}ZBep)SwqHrn9I;jnt-U57Dj7IlId7vCDAeJw$CH5cd_N0&rJji*N*U7~Rjo8_3;#4jj7juhRm&**9w33x)47=n5eWQH!)LI3FCoy6Zy3`F_FQ!t>@brl5=EuTDHAj2I%-4s^ViSQZ}XDH5t1Y8H;px9!l?P-4_(wchv(lilRPE5aV-kn<)q2}d8$yIG-F@^4T^~jr^qQtD7l=fx@LNRYyKNiUeUNIhD%1rox43LUy!CiXp*LhlN@y<a&;*UIJ4kt7pscgHB!noF$HcJrxBm@N{|Q&-aufL5;sa0znax+@S@seHTYn+MuH!nM#D4Lo{ub<y0Swg@e7?d)7jBkmdY8+KZNhInw%P~#z)byBuk2?Q`#l-Og1DWy%U!ct;Ro<&w&bFDj=O;M(Y|sBCA;Au``Do;~VpBf=G=j<M|Q;VISm02D@fSTLNRUM9BvyXlU27>zV6SMd!3mK4m*zUv@02oi4_~=-Sl1Vd89IEQm!SQXyBu^)3nhl9#T@V=4ffxZfEWuT1m+3tW$fOHOJ+&X8rH5*{qq*bwt8W%)m))nMg|#UZr1;QnCWY;ztey1u2Ncf@zIge0#86G@l*;6?>Sxd@XbUNo0h%uS_FNb0C+K@L%dPl+B1us(0H1`nV<S_-9|G8mYWrGY8%IBr%Y5%{$n<ibr?KQ$atc(t8Rl8`{y+)A>)DsI>^lR~9o%1#%LFfn3YeO1qCT_l+a8W&3}w?yk|wf1msZBJI3g{ljb5)4ILzGZ2)D>&BQ@a#0rhA381%>Fw>x2SgG3;XYCa#$;bT1fIgq&80wI_{qOpCP~5<NzbYYn4RL5(4_B@xKb^Lv}+AErB#$U<3v+IpUXo^&`>8Fb=r(Xtmi!zPwtERt(o?Xcpj*CcJ@K+(;l%vY`r++JX89@}0TQpXJ36J#JJcF;+vVSV`ex2Qvi_0g8n<c_PL7&W8F}`frImu~cj)Ko5f`c(rgIgrY6$GcZRZ5s)`xZo%nxWDtxO(q>e83ZR@e$gRz=5PegyC*o17G>tnfDy}nEtY9Y%KF~3u`2v3YM}#!2;Z*7L$bVU=z8;}Hw0r_Xoj@d|9FPdt3Nk+okJ>>30&sAxD{l6|-1@o0L*I8<xXFO)as8chJ-T$m@`_<CG8U)&7F3Un^qERuitQB7L*A@yyaA=J!N5#LKaRP~9pDJqv-X7fZtiwry@qb%DNSNm@(CsA5-5Z)BC4g3uAKx}>JprW?S*K)4xOZmHL|J&glM4iwWwBln%tpOLu5x(1PO4_nwDCafF5%jiFN6uxu!~4G|U_1VZpOTt4G<$gVU>>ia~Uqev@Mnm&c$~UAKbvaZa)xXkKg$R<=r2P>G&ieKAT<W7v+K5eAofjo{7QU405xj+7RtIKY4fn=~Sh|BW;Lt#Zgw(4PVjwtH7}4J#~51gP?FHPly%dB^VAQiOe&@e;3hz6YcM$wL8U(;b}$S}2P0+Y-bHfkxXZ_K14Me#ItdF!5&X*XJNH2!GEkbS&N*C0qLC)eD6$R28^TXqD%Z<|Ioi1F8jDm6f9-N~%A+d=>YkUCLmH`pjy2h$q!At9a1tyJbhbGWx?bP2L9dQv)3$BY-OgB%@Sns!twQiMqw$x<+S5B*!$D3he_2DTzJ+@d~5PYUxV<*1mQ!dO$%1pnHxsMuz3mS$5&7tri1L&BswxNmXAhJ3lYQc1hLwi&PN@Bh$=Dos;*eI2PC2L|q7Ut<Y#aPk+z&yk3S-*@aO1;v^ljWKBdsfFHJ=&9@m`Rg|El5Gs#p^m7{7#$mOlrN7yR0Pc$tkEh;{CM_sdZcR?el~E=MA@q<=pchpk36Oml*#sN~VK7lYPs}&4xd<z9cR)*2L->il?7(-@w116dc8Pto+BJIKO3b3^cP#CcK_WcQC(oO>c7So9O;q;h<EMXS5~(p{WA!E{t%-dcrkBeAEUFo6ck3#jZlxMEJgQ>Jw)#oa*ZKZwt+lc9hKeDb*X2gbSM<T^3V!->rw@>>>usJJrS>~1wo`rYY*s<%Zr*XX&Lv1F9`p(tI}vOU@wQRI9;!%kIZe$GOc!-J<-sX>x`(31kr3t)njX~7$dq_!tUW+VUAC$0<o~YTJ(t^F*;kqs4v7S|?{S@ybk!X}BL1Q#0Ew})kyu(wWfVhzhi@UmSL!O@$RvjtPfGhLH7N^YVNs|`%N%3>sUkbeOf|{~g#}(VHxg_3wx+sL20~BQ)OkY{9>V>>!6-!*L)YW-&oZS8l&ztt$nZ`j!sSevC{ZvyE-VWs!p~R{O1XM^ZfXe*Y~;zqzi{NNj#==OK^CV1Dl{?=X<IlhE;A=Y@g;0e_khLJSON0|<Q+p~_&N$L#o{(pE!r!>O84`0({>r3WBg#<u*5m9{#cv1%XzX?wR+5w=tvs4Z3+D_rY4E)(5^XE1Sb_3nuvUMRRlIx-)rXK>i}MIrPsQqz;qNdFU!r!H`FpdnqaP22c=cYI91T*6`-$RQR$Mv)pgj_X_Qx<nX^}cV>-;5f=jridl^V9gUIdaQy$P2x%m|!O!5)+PFyy@S{yN~QsW7J)CU=|fGvQhR5RH`ePLBUf@3R-#`?fw5db<duC&O^SWn?;!X<iQSgW3L>i2^nKUmjEUpF*B5}65IdqQ(`H7Hehgnt7v083Ful96-;Pw8=i1ICRv;Fi9*pUqjW5w2Sv54V<dCzY|)E;6M60nM0`70p|8%&*ee04ECvzzBf?SQRU`U<XZ6HP0bh;z27i=a(i}5Y~R6v>Zy&@v5+g)|U)C9t25HcP;yyAco3*rlhlS%HSp6Mc_=<&bLZi>&k_dgIHT!Z5Y%|0X5Z7sZ|9gOCvmBX?@SA)CO4|RQ-yU7!#VEaMuQCP7!Rzjl|!I;777lDr1U4TTReI6qpiC*<=ph*DhdXf`+*SM=g0y7v*kaTlKKD*}R3cBX;7m_1T5o1rqy+HgiHK-Qg<=JvwgyWpzD!BEJ^OQ?qj~6*N+Uc!Zc&A+QhdsB6hE>Nks^cEq)lBxs1|>#}Ba8>Xgm?&JwV|BrL7<jddpNm8C}MnaBa&h^aIHXehpp(=t`#RAmB0W4_PkVCkLS)`@C0YVcXE*DBy;LE8#Yra}jdCbqVxLss<;{S?4Cp$|YOyZ4`^sU11GNQzeo>X^MDPTJy$H6TLR&toVn<NV9mIoDcBCBg1A(Ua+^1fy1ZhF*lizZl$*+t2(MPAx!8)6i-BELB6^*mdpf=8G%opVjY42{E0;4c)v?O0JV6kNuRv{o0hK3)p#H=j|eL94WfCEQw*7Bt+3uIOD!6szh#&#vE-COZ{ytDD8IO(M%fLu&Dx&AKa_%uv|R=}&R^Wr|eDY-S*x038bJlKx2f`D<F_=X97l2bh@K6OnE3w*Uc*CD8j+nTtFdmkTuwjgZoag8a~OS=31iJ=EO@7OD#ZQaWLknBzBJT13aqs-GHo3Zi2Pp@)8_$U>q}7rRR}he=&VRv~h*g6n>uk@sH5TE=T2A@3N}PJ|~E(?G0Y=!{{&4%1p%by61_9z9}WALSPqVC99A<pLr8fHoy1EhqesD|hv9Y7yvA4T+-(J$p|ph2O7)9ln1-#Z(|ZZO!E?c~f8az{CAhx+WWjjC0;E!PdC2P%L3Cn^<k|-LB8OF*QY`SSW2MxK22q0k&D?Kqa->8YKEO%qgC1dhNCqnQQ?qOaHRm%WMc@K&yTnWi`S8RI|vB02gKq<5_f9L@6<>hO;*SrRec8KO{+|v1<c3Jz>V3fNtM;5y%oioD^S+NYoo4S^hOd$-??i2JjS?xnl$&F`la7ZeH#wC(K!*U{pq?5}Ht!(`GUboiKsn2v}5qJGRUhE%U8qFn~~<HPTn*JTDjYG6w`I$_#PBMw6<UcgJT?pxUy;ztD?ns)Q^r86uwRi#GgG%TH7ewKf>FYQ~D@P6E%2FymCoh86%})wanMowifb<0@PMMD(3jRL}4qS9}HR@`5fhT5kc-Cn%uJ(h$_iy|LzY-X@5~xdPEz4(m3xxu%_Z7NjE3Z1dW-HP7Z+=`u30mnqFSy4B9Z6lp=xWh%-Z^I6y-Q+ACCWU32t(cO$H?M4w1XRDFG@O>tV#cANnF}*BgIM8%oo02%QW=|-TVrGT&Av&yZED_&+OV)UM`fhZYuj(@0tQ*$rtnFr`t_?|$l>~gM%bu!UrloG`YW*qihv&c0pb-yEF><a?Mz}F=&}=5ZUXMJe!YZkEv`)E>;LfK;aBDkM$2P08IeSZ7NDv}?6B2to0KYcS=xPre@i7wu6yYVK62p9(t^FD~Lut%22z&}Fu*yZ>CQ8E^S%5OTQm%Td2{PChT)8NtzD4t@uaGvls}av-mmB4V3Ca9%;fKzbnl23xQMQ3|rPsOOt9^3VmL<k=J&Bk#LN(B=5^MGrC0+x;7Gs4>8^7>ynw67{$S-uE2rZhQ*5!CzK&Ll3V1U<iF9{<w-B&zzy*kf*yhc{8mQ!CSyQliqYkPxYO%Ixkr$;@F@)I7YllA@>dtIAA319C6>Fi=1soT<9$6~d|@az(})xDutk(Z3CG1Lp_R@36mD>94@_|((V5DFX)LpwDmE#cj&i;PLnQo^+oQ*nZPGB#`22!5qetqi)l{Z{6EnXblK&Jqisf}N<&Wd>_rY8y0Mr30^_OrG<~en_DPL7Ll{-dP6>HN%YI1*_6EZ5FRic0D=i6~Dd%RC@6Sq0(38yEYWzb)@gpkf<TbWysYW?krSv_i93hYg`S@p~^K^;Y}=<?y3EeShX!7-@;JsB>s3VDSEKhuX@F6sX-Soek_i$US+ov?R29R*(CKNnky76+aME90ykB{rZ%1Cs*G{J1Y5L4QzGQ{sJ*%BO*R7s5+ox%VuRCNo2bzur9LIj(qx>^sC!gpeoc*-D8x!y8_*$tr{tPqbh8BqV-y|vQt?@F^T|RfffuP13}CKln*`#j4G1!sqgtVssIFfMvVB>SSI%*i#!?u$bR)`=h9N_F6dFS=Y(WRf!(2&`^R`|~l9XC=1@c?~|FZ6RALLReWJ$`o`zRo-i!0i;KDOzxWHn%jun-v1#{&=q@bkH%^B#z<BHqcw@a6ND(b{^*JgD;uKr>e9Qfz*)r)L*f<Z>c5$zm$F^Q3<0r5xVceYIB@`F~K$rV{{iOd=RHaZ&veEKT^kYGf(J9bHzZi=3RL+XVxeFslL^b7}ODSzGY^5ydbnqak39GKJD${<E}KCCjrZEx%S)%d_^K>Obg;5>p_p9!PAxa_z)|r$CF-A`lI?XF3SKVTztI#u``mwOM?<k`Tdx8%_<geiCH8UGuM+OmPwuU@jvo=`Bk31r+s#tA&>+rDEmhv&gezf5y`#RLAzN4zM(VlPOhOmCeqs9utJe%LA?in)gLq<Z8%0!#ThM;zX42<e==HI?-_IfKC|$c1tpBTuHQ^T=S^bXz?MG<n!W?T^5^2pu!EWN=q`Q{P<6M@AT!I>7uJNZaZ9CY6<yT;d!O}?aMLKc?VtOF_euYNlx}vC-U(kk57{zDNi&$oyXd&Dry$F`83w3R)1w3repfO2vh!=N-ssBS#7e2hG$CgoO1tdYa@`&-w2|JXf<}3zFsNXvz1;z`j4cgSq9*$49xkPVIc-80_z&w7@BDWY2d81sJvW9E?z(<jP>|Jju($ni)STF6K7x)Y?i}i0%xWP_ep``Bn1+t81Up$;aFT|@<d5ACeC=x@OrEs5R^#^d74%q@tmq8naeh?qF73LF>Jlkoi7`ZA<U4hB3g?n%O2^H(qCRU*#gh;$s5k7)LR22mx`7u1SUm2t+my*#G+r-X`?}{f}h6rfiId!hBvswMV4oqdRZA^2a`Y+4Y8N3MMJdZ;42hOErBbfUD8$+ST})6L43s2a|Q{Q<O(ZaOzo|laXuHkZk2jB?88A%fhXG#L4vUV4LQjYWGv-BDjPs3R+cz0y()>B!XIV%qDVI)-I+ydKkgS9xYv|RxO~v*1A9ygjlu*4psSp`61UnoB8RGEmvUOL{JU!W4xjkrNk9uRJu%B($W;~DoY(RI0O&LC4Re+A@CGX{*Y2j}BsG~?YBuvn6=X$AnbqrywrjJ&fn7A~C1+bsC|S*<Fo0%B*1gvQmgdxyQAlg%vgn{LBWWGeh+q@QRDf1eP3YJ&4G>B_odS$0v?z4}7q-e+mDZq=q_v*-1xiHbH4?iwS5eYn5Vzv>h*GO(BUZu)REE&tO4y6yU&O4Yf84sakB?e?h;dV`=E;*fFh}<-qfI>g(Nu_)s0UODt7zWQLo5Dt_#p5aOQ7K8pV8E^(Mo)1Y!)nV`UcvC4~n<YvMz0SZ`FIN-e9Z7aWVGKm!-#A<7<@FudbW?*g)<)P%Cv(pA6RTMvmpzYmj*cO(>=m41{HF!ZCM67^@*-@?yZmW5y8`LZreCu@@Z6LPcyWW{?SW$%%Owfw<OW6U#J{fN#t;c{As$fwnMtUI!JAhL$dQ#jj+6hK~>TpX*jLg-U4@yC{NUC^d*CnWz?H4a@)*7p}mhpU(g=;2#u2QHf#|_i@-;gk6BQglhBNy~3(IF_e^&M-8C`PCotyeMS4aS7#+rqRIM7&(B<EcL!D=p|L;J2IPkQSG5n~IaZpY`;+Y=Ho`%>4*RV<i8qx)keSV>soTGA{||QnE?W')).decode('utf-8'))
_LEGACY_ACTIONS_6C12S_4Q_SECOND_YARN = json.loads(zlib.decompress(base64.b85decode('c-rk<U2j`ia{MoP)`Lk=5|uZN&D}9pGcsg*h0Q=143G^11e=FR-h%x1IFd+S-cwy&)#p(5IC{ILDc<vax~r?JfBEl|fBo(EfBgOTlYjc<<cH7iZ{Gd-;ripJ&v%=XhtrdP`|Use<v+jt&zHx4{Pz35|NXzdJpXd?<NL?|)gFHM{I_4Pe}4bd_07rY$=loelhbAM@y8!Gn-7!!__*1;`||PqkDKdHC#RRQkAK?S-2QxWy4ZdF!`<z>&u>5N|Kj4|;eSr29sBV9?O#5B*uQBp>Dw<S_nVKO9^3l!?cJvzAD?y~%^nU1;^XG#X8+c+`CGR?H+dCk$n>@Qr}<Q%2FzX;&K~UHt|gCivN-7L^S8*mKHOZt-9+Pw`m_B5@U~gI$y=ZQWICQrJ03s#dA}GA`uaRm!Pn9e-dxY$zh55LpEh^%MKu5HaP`2YyPPkgkGG%ai>O_kfBL_jaq!8kcWf%#!8sh@*(mM%_xAdEX>Pytv@<7Nx8`y`T<uG@qcHteI$dD@p~(R|p;^J?Eze^Q#%wYi&5X6*(P!*=-09FA{O)|`?T4_PreIwzgu@MNhVW?RXUjnsw2?)JPCj|tmg-|Ef0EB57{cch2Fy`5Z~7qa-m!c5a`t{i58lA-$Gzu=pT9{beeCbk2_Mpd?cYw`H1v1Vhp+Invs>jXuqKnk)VM&#{ObH{b++$|w_t9Mkgqmo#F!Smy}h~Fy#4g+pEh@&-rv0c=fg8$(BPF{Vl0vJJB~C5+gp3mo^TKC9Ff_VgRA`f!LR_o>Gf~S@4Szzx_6t}f1Nf7Fz*`kabkpng<J76fH4C11n$-I(zeWG-iK*#vp%K+2poIEAZ4x!e9C^1jRks2e~@_uqW#$6kH$?dI#BVTO17`Efv9hu&p+{W`dnWHcuIc`ddr6M0F3+nPqxNjzWH0=gxHpO`>dZ!O;v)My|7{Z`fKBVO}_Vm4Yg81?z&+R+Y0UBd<dg2X0Z5|Q}6B;AvMx*$gW!HkgV7bySGjbEdTBl+uqYTYX}jt-gPI?`?bs1pcidrShyV%LXnQsl(pY5o2cbMOooCzMi>1a^-Hl)f?g$qkwb>g!8?btz8~P~^=Dsy_7C{8I)F98)QKbSFod5%PUkj&5`^U2cQ+m^bLTXCrRX&pcuHRYGP8&(Ac%)bIqfG=^<GDoUGTx!{CIu$*QjITZhQkR5Tn>=sCIoR4$*WhdMF0%;IuKw9hsmDNa2IN>)6v<y+KDt)oxIxBbCD;0AD#+cKbED9h7~<Qy%pFFQThv`o4*Qu46EBjt0HYz#A$N=JtnMn$)Y=@cOg8AkledIX!=G{kYv*W9l3e9~X{k^=!m^{B(DH|HJ0)?r*@7DIrX0hr+i*8s>61+{79fG-B~^1T^XeK`86)G|b336ji-TV`QNUJRQr#np!7QtjR-|IH=OKK6VegD?R@?4QJcl$dgTr$*%)Lon79^d<2TCAnLdE@l!La79o0iYG@_I+TL=6@FsAzou8|~gh!*}y#}_vR+#L<!H&*5?V7WP!tp7@%Mu%b7%J#^Rh((+t7l+L<yv8A#pDvazrDSAOpAf0)$@NoPtce1@!d(;*4z8@xVOf~($T4zgN!0Eh_f;u>gZOG4c^09vDfl$B1BLQ#*!}u_7BKZ8f_?)ril3=T6|2suO%3&iyo%?E`98%Hu{+&WfFSZJeBdzO_U$uH4(t3^Kh)!M1(R<I8%p-1>L*A=zKff=;)iD7L{$lh8aESg91*S7C@e-&eRxRz$clRx5u)gF3fD%MJZwj%&!HG*{yP`3}&<1rkY5n(wty9^flvLcwh<2>;;*qK^wr;%&s~e$xwXlY=DA~+gm>PB8MB)vxH4H%;wEgw>|4Yy3=X4UQ7d1;06Ys?V?Tw5(wu1I?1+Xr1D*0iex({xu-pr1=~S1`Bcv}XZfx63WR^qX&lc6G9`e4G1G5g;$O6ZVK5bO8;f9M7%s*=W%f<Q*Z|f+6QXUh;jIyGJ0Ds)r{e#W$d>FK?L%qA+r>@BlDwQH3Io))JD(=ELEHbc&O0`&v}^27ijGnX@&ed5fZW;t*U~&dItsvz+ZOiamdNShUmo7Q|Fem~0{dD|9IwH?fFq*$Dg8{r#T)E)G+^-7hWP3I&0h{(D(G+_D*=9ug~NC6I<o6^mP1Lq>lImbx+Umx^a3Xgl8S&a7&#Zst*tOTIUZGqCv<4O;%Vx?o}SBW3xM?zyf0fUt+jgK)|1Q#Wh)5;jq3(K23kYN;gFqMMRQ7aQ7PeCT|AmsSpvW{Mn~(|?+top^I!sDA2Qjx62RalVJ@x$7CS{|TH7^=a{zCMIYF5AY1&D|RcHqiwVt@nFizG(4pq?S(<D~Y=ni;u3Yeu}Y64@H3@zFQU^8`F!6;_I_2)nnrz@|e8CUFN&{auls+H?&K575Fl2)+StBc<qGL^IQkhKiixr++xhrKr^TOa(Alsh9dayRQ<LnM!;kPZpvc!(1<K7(?|!)s&y@Qvw?86GmE&#Ag@S<HZG+3uwkum~Xeo+e{8P=cYg&vb8^aCp5CXHM}R;!%^}pG694e4#T57QnWKnps(tg&Lg12>|ikDnS7i<T+Qcne=buHwm!96V+^mS0J*mD<BAe;{1~XO5DoG=WTkJxMPVj292*3T5hEYIQSUNh-k?golZJ;#QEqF|B?%1s7KR%3|E2$5NGHH(e#Kh*GHuy5iu5vWD!`}vp(1+p=L~CHDcUc^SE?g7V%a2szbDn*w#a9xzIL{^t*inakeC_7N*)#$I+R?NBps|b~I^LZPbRe3YpEv85-WK`oVK-*GSSfxweJ*zV3?qimd_`>$lLX*M&7;cj{QdG5!4RAp0@g`AT$L3_|PCapK4y!0o;(uX*sYmAo#cumr&ai$`4Xbt?=qJuI%f=TVmgp++ykp9R7t=MRS!%Nhh!gE4!Tgh$1`cx~1}+%ucJR2hmUg?7#~9j@t1#ISp(fHZdzNrDHCYy(gNW!nMxcd;<;0Q}0f-SB%zjg!~!0?oZNZUl|mAaP8=7R*QX@<HdHveBe|Gf4rAQmS!l*C^7VcL2Q|?_$QeC9qYg2Ny9ra`9l$0MJqbP1W!&35v~orb94Pxh~l#J7(OpCS)xA=Jn;^N0a`6oZU%vJkmzcJN^gc+DGKb!@ew6fn?Ppt{1a7H?qys)~UH#G-Vif;mw1dLBz>K6jFtJEihqZ$)T0SyV4=@$tIvmy6w^YLc<&t<4kQzT@R6mi9#CCG|wWO<Y**SodL8g1SMOq)Eq0}(SuuLlp&YkfHp@$$X_<%B_r7R%d;vv!XcAy1u2PY3|mg|(J2sn^qyv$gB|NR{Q31%<XQtKPry$kKR?UCo{m&SUa0k_s~}2|%MpCs+Dg-&>Pf!JvQtx47}+-MhK$@@S!pd4USQb;)KoB(^}NuSyxgeIN$A58)5BBdY1RvKsc1u}lU<|hGJUR=;KNcTD9IgYX$)B+0Cz;PER=L|<OL#417nd<r-LmVPUz@dIH1LBrN<n8O??v%_U1T?s@=o;el!*BXRnfr?SySdd#k#v2sbN93{jew)<23|^C04MD)mXB!{qCo6XALnRCNbos7FgO3X4T`EHdMiO7{b6G0!xMv0{773D=L~p@L#v0$dEg=<L<X@~7+$I_n0uOHNl)YQ6e1;}->D)h6)3OL)r5t|Jc+>U^-)hz$bm0Ut>#ZvYT966<kMq2t3o0RMsF!9*8tIs@x&HP+qHtS7tFX(tTf%^MHXTiOG<%?wFlktCR_$s*ggV!J5zlQ9&h2}2JxA3JNMKJE+z<(NZ-U8RIasDamt3MLq+8oNDzs8Ho=X-<gfkABDz8esAaEKy5U6)@xqNzMkqS~$=ki*UAa@|uVrPvKEAwg^{6Nb=N~93muzM!Fq7N)V`oRHVe9JeOx2T@Vb?1ny8TOJ|&z<BPe1_*1?^=19j-OpXaqBo2F2s1J)7iTmT+KuJU)5H36eI<DR*YV4XV6TYE!<wH#alb3KymJve}x%Zl_`k1@sua~%J5?Y=bK?C5=vO}&=C&jW{!eJ$Mi5<g1qsxn(!uKXPQylQq-g3zrO-lc^zeon-3X8>*>i3wm4akj`Url0T1mN&uL=$FzbLatN3_CIhKF6f>8TwTyTA!`KPlz|yD@_j*k1|CLN_8-EMm#90zgm<s6BY2H6VqZe5=pX!?S*Q}PP<A}xeIEZ6bc*B{5=MV=p-A?z3C(er74E$xVD#Mu_T(sf^OF<8(?;U`}W7`VUUBZineT#jTzB8EA5I61><s2v^0}s&p5%u%1@_BvK+*qCZ|!`j5P{XcVK7_vW-*et_q|m0xRlfFAbdLFH887%AwkfsT(2Q9(2`>8Zt2uu6W^6)<UgVlh`EMHnDJZk!Zw<+#ydKwM&8&i~)6pa@EfQn5jjRDePV2Aozq75m(TQg1mrQrqP(1zkk)Z^$`NF`rbGL1-C3f=CkbmPEW}RD#G;8v89DuJKEI9=<ZJ;;wbwiy1IoP4KK`jF;ypyNA`QfZl&F<I0+1q^!deMeUImVW+@*-y&GLL*H+r7)dobBLaY>?+K!{<>*3VY>SHTX6529N<RZFcAymQF$`ph5?x|PV0QU*Yh;E7?jZ)KE1;l>QORsoIGT|zLkqv&JG~~eHk-YC>d29}LvP7I5T-2Nu7_MhNe&xk9X@sT};N7QUXo~-%RjW}#(F16cN=ixMif@kN-$dTbIre+Lb^iw0QQt&_5@C;G5U(Qxo<%3sq-3yvsKMs4q16zi@|*|`j*z}rIMF(&tc%PE40fIrUerjF)>7JG-Cq*NPA944iSSI998mAtxX|Q)q_&kLEvKjzwP&+_SJR_F=fSfObl=Qb6(6<gj&xSit>=q@T^O?bZ4!v3@xc@^Thl^cWr85#{%6~45bABH4v4LyxHxmjx^n7@T8M%cR!|X?rIS%lb7tL<XDLO6c9S)4<!gC$<cVHm-iLE%(NEim+)B~m=E)-^`N2Xym(E(_+1U~=xlg@w>D&*{{S64z8!xH5a6EzDtla9r34$S!XKB=O&@^2LbYLDX!W)cIpN44hqTZ~9MaM2)hK68u((vnyfZsP|YXMgg0Umz5X$z61&>4M#WOYTLPoq$Xn@IpANA^$2S{jzl-&9{hq@cb|jzPN)etRm|xQ=N3tH#$l{Ae->Wt<63%{N2eFDU&1zkt&LSTb)X%@!y$)g=PB&*(7&0kBXB-BMz{3&kO8P>t56Ev3+c1-OwsZ7qa5?`N@QT>(K2d8(a=WBZW6qKU~+QC4Uk_?;f*%+}J-(^biB`55N&DUY)Ko<g16>o|;^>Es_KpJ_C1rfPkW=36uKd-o#_^j8#q)gd)!leU&J0V#AL;loMJt}a`NMzdY{p%x{s3&LMp*8v`{JcLb)19b}|QpX1!8?;tI=;_(*VqT{_UP(@W8flIvPfN4jy*4<(`U<|R9x7Wi)09ZQNS1y~78Z!zQtcL&%|Q|kY-NL|z>^}}-@8JR6s>4_#`OU0e?`_5@>yi2kJaYosB#Gr1>`F5b7z&wUs)l96#~t17QFi!oDjwa6`W<5rG8eW^LaVy_c9{{+%D{%>?F^l(5PjuM*Ts^T7Rzls8n^}e#?HuGrG1Ek$rfgO@BiP%hM7FYOPhH{G*fW-IaIBY6@_OAahM<&B0DA0XU8AaLa;`eQ5)50j-TP3BZdK3bCbBgnEU#wPRc|?nqK`Akk{}2~SrJsiR%yVR^iZd9NgAyR2E2m|KgBl2#jI+^F(~sy=_Hdn8t()RgT@#geI?5ZmEnLiQ{Lfo>_`@;_XYne<zs_Mt)?A^9a-dW@aQjJv}sB-ZL8*6Kx2%!lGY3SnVLVaky#uM{13aSo6ROVAieVK1XyiDWAo^f(hCg9KoeN+j`m>{LR8<+B<azglZWCG7dRN`t$o@+D}<mcVNSaN8Yak6eT^S3s2sUzp{ITWN!U8V`0W4+dzOPiFDck!yK1tjeguC7FO^FkAXn^^u`xNs=h79CT#J%tLLeQgc8PqLG3uay=NTRuoqtS`>A(O<_OOilUB@h?G3|BV}Symrsu|ODFnRPf(-P7#fMbx+6=B9^)1&Nm%Wk3!<ae8rL$2>phb)vUHtWt<oT1ry0|wC#ST*n@s)Inwv1%B2JB{Ipn2l0n;`Tg^_{S(lpJD)RkbQl6?k_O4WX)>5-f;fjbvxq%N$KmUew&PhMp0jGeEgFkgfo0B$sx%0u(&1%C;w=sqVyxbuK7CD;98E|gpwal}<{)y()=xf%fB@k)g#+4T>}=(_{$_;VdgfHakYwHzO|ln;+;_RV+i|J-foT-7s9#FFLgxZ<Z;+jk=)>XJ>c2qwfwn=++}PRzcu+sR~Q-+ICTR~=+2jpilPAubn^c^sWmzt6;!v38U5l-~^xb13<Nxp;1u6}c39&a2W;FmTM%5za3q@7_%jrVCW~sJMK45zZ-^`4s;+fHRk2knOCo4ouakE(`fPLqBcq;Ovv*^98M(G*Pt3Q#~uP1u>~5v%N)*;dttxhi`)8_Zwsg77Ov-Z(K*Iq8CbYfnxF&3&rEG^)QL)DhH5tVk4R8v2hJtMpMj~U>@>9QtN{DPs+kz2cjg&jj)W2oIwr3*Fm-P)u`U{0l9a@a@(|eHnb~Eu(ja1XX%?PM>-WO(Q49Y>OYapio$C$0tixozM#8gi21N;UZ?>{*f`_R34`t|D0VWVA;pV`0b5-DMit%5aa$NiCLkUKbi~``ShGTpHx@Jyojd7CC~sbz6$(V)4Imie^{H9*;pFLEM{=#z!>TUJqwF1~37yrRODaVL8A4OlW;fK`R=SxNu<c}fo7QFw50Z$1G>`pIr^N-N`_e5d6~0I@R+r_lO-IE~z85EE<4#&i#QDx-m~S-}9lHqN<3C~{s6(l&<*|^v*3AP(+Pu+c;fIAk2}RlZATt-sW0K62+LhO8Ai-82laY&hSZd{!nmGZoNEreun^dhBRV%~7&%4Z_)@9<wj&<s7aS3?Jx!L5fObGx(D#_|{p7aZIo&eLv#%7rLap|0qt;r-M&?cU+UhKL9{z?;Z^~wo)5Q4in<KRnT;xkHNBpDJ_sM=UHe8Sjv%@HHn&3wS~GF!k%bhpu35xj<yLps4&cSU(bJQ9Es3@FOCkYJcxPL5;cC62p7<z)I+sG^gI-ZRml&@wQNzBg9(Sd#hX0x?*0Pv^Rw)$+hHJc$aB6COo)(eY!gB9xXu!f2P^Z^l&pY$A;I>-o9?huaJ_<)eOS)uGlXPTH}>r%)X93ri4#SHsLS?Xndnv60ObR=R0{^pr%FRsc7mjHl1eRaj>`N2n<IS0==Z*tiNWMhTz--_FLUfDqDlmHc7r_yPE>uP?{0@AqQasH!A&Vr7(pnwP8V7kweCSyC?4UP?ACa+m7A3?^2PgUZc5FA0^)Rp;5-84xz)wiuInn$2)<S|oW|Pi?D#5qf5zm6m!h7Ej6!83$epb2EJBk<|&Trs5|zL0}bz3wTyUt+FXKT1>JyS;oT52haO)fr;Qjgsy}o0-kJ|FHYyk)O2teHVfsz)yfsNYZ>tDcxTaB9eA<D%?U+NM1+f#Jfx-E>BVD3tp;UF7WS@Dk2ENAyw!-Ei_#?eO2y(~2k~%gmoJ@NUN9RHDqSYIaNju?mwmbGGS!{IBAV=2rQYYd)H|6gOHV2>jlJ{u!i#n_LO@K)Wt0TskO@{k$k#P1E2FWBvkF&lbCO*SkO)h6>FLNSAv7Z7)o-qp3$M`=`L@g1b~1ap;=5KCs)*>dhYGT<c=6KC;*L=&!w8}xZ?DKfVz<xW6URnB4?N>VTfy-%vR<OI;5*moBX?cFex0}QJp2$YME%eC7VBs4wb^o#UNb4B78l|h&gC--8SsOQ=GPV3ds&m5tX!SSN7%<TQXgZnONeGdcOR3VON{U=cam2m^@ZM;ZEghc5l-8#W}dl5H>FEFS{U#v6N}etjvx+#>Nk1?wp|(=(~2h*f@$79Bb6j|Z;ebON3u#=f?OP*Mxjd-tMeL_$CL*U8KsH>zAA$_z4pa@27{8!kYy(^7xpo8;*uh3SEX`#h^(wtiV!O}aHHNPZM3V9vqpBSZmW6~;qp1MZ61JWs$W$zpOLS&1MsEWcel})hy-;fP>y`G^O2oSq7hm9QwjmsFHIRGml0FvO+E<Eb0t?%&`Jy>>OTaD5fiahDXsHrGBT@@D-}@iYsrRa|51hT$U!Z!T*PA<9s1i-aR~HFq+CU1JXSVB;~8qYf5G$%R8x}rxQ@<%j-^4tNc6OwP>nUq%}co8`r;zV0^sMqm>9;_z9PRcNaA*>?th!6`8<5*4Mw?UM4#`3z4>&f9+keCh000LrI76sOCA>3ovP}eRo;Ns>|L8Vn1a8ogL4)Qv{<0TL0y&AHMW#U?$GoCgRMI~eqH8ZR%d+`1*&qCsI}@;a2b+^0^c#0SUES2z^v&$?935^TG<;VHcb|#O4Co)Y+iloIsDstgrZk**~flt&8Ze7r4>-Kxjl?;uY;u$S9%wR;YuM2u8mb51n4h>G(Sq*b>YcKFNvVd7sfgd1xw_@2m+Eh1pOx{7wZIu^YM)EGGl!qfU~~-#5!CnCz;5cqnJS+vq+4flv<vX5y<mdl{89Eg9PTD;67hYqN=;@Vb60o+ckLUu%Qz^r34rnhG!RuW~@1$cEXTwohChuOQ(SYjN2@71!Fp-$o2Q@3oI?eWnB&nXgqK2(#vv@_<T#zfOTKk4&W2GsYLy;ss1u#zSqSFa!~~qgt^eR-S)Mk>WP<`a8a)j0)(&%*yjZP#km}D?5|FRUXPD)b#XVtNjoM0x<as~`Qfqnn3hi17)~jpW?uN3(`|&Mo!5djmlVxN@*EjFVChY9h3tazVg^h&$%`d~=CYJLpyvL|3?iayP&`F?v>?P7L06`Kr`VR1Fl~uUw8Makb?P-?%W>&dX-THod0W3YkasF%Yz~~l(;h`k8W&>%IDxtntJs_x*UPIu1&YIVD5PxUCC(~hj;zT8wpY4Pnr#=4JkFkAuJOjc&?F6aR@<7()S1O;6%EUBZBioEN%Mon9KMktE0tLT{)b%)sofMtSoo}>szWMMQCvGOk1#}+lDWJf52EGkYn3#(Vw9Y7u&nQb!kr$~URA5Ej}fShFMOeBY7p)s)T_3KD(R)|%&PBF=g^r}ewLuaQV-42s=Q+GMwe2wD6XzN*jarWQC(B7P)J<mxsHbQW*x}>k6qhFF&7FeP+_Q2@g!j8GWz~@(h@b{-V=Q}NGNg%?!b%x2Z_%|6ohoWWYmQ*nvm79wy{LQu!6jKfZu6+2DX%(IFDso$9wQ{iuD#WZB$i;wr8d3G^*a3zPSwKsz&_-o{}gRkE#}=Dvm3I`Xy2Pcxg^>Wbt^p8ZEpW#NLD1<sMBm!SY*$hEhcng@*@H@ieqet9U}9Dyu%6o0Phy@;B+6=_h+u*0(Gp$Cz|{o>B>Y$7jFlqnG6;sg@@ru$9UiqFC3RWcG0`P)wa6J7pO%$@)r^WbB>L+i{dvY_6HASVzQts9Xsx>L@XiiaGyhW$G1!tf@AiR5+lPZ&!<JStU_L`4a|J7?rawZGO$dsXl6hT$HL>%#nQ4kt9o8r3UmN>7ZhggS6+;^?2HW`WqE&_0>zskx$bjGG6=0kp4o}5KFfjiLE<$K7tsxl9(_pD#l<nO1KV#)nk|ueYCYVl!L#e&@H>kZTe>X`c;Ley!V#@=)^o<w9JHLg!P!xEl&1s4%9`)HOkw%tmY>y`uJZKSXPmiQ>9*(%R#)bq5Y8AMQ*b1g%M>`mT-R|4MV7IqcTgeK~@6=b>T_P?dAhgWW2080YjZ)s+4Z7a^0>5A&DthL5mJE>V_136hJC3r<WD@NaB@R4cqj%)CGb<%ZJ7s6l7A>h5@RWG3#MaZR-|D$lwrKJe^ki?5t|Zn4U@UCMyoqz{NA8*eWHev^v?ZXnciA?mTt4k~n)W5I8||fXUR_g;q37Nu|i@dud>&lSbi`4cR@2KuDzg$lZmy9Ihk#m{;M}Fc7Ab+eLz`CUeruhld`y(`IV@9;r}nlny{t7jg;1A=<vwuqBRemWiqA7(W6$BW8q<&(dNu>`0aM0wWOJ>D)e7vTwc7Vt&*-A3#1oT8ZLBRu_~*Ily0It+hXr99|QA{AP<8b2kV!$tqltu%3$bMP)3=NvusGE|!v=7QR-%bw*38jG2-`YgVF=giMO1cWF$)s5VumWdW_N){UnQ7q+|y!GBk^LdarqjQk`CKN>}pQ_30x?~jyjiI)GdW<;sBP0MaGci}z{4R<adozW)b|49OVeQJuUvVTLUN#ws2ij!K2Q}>*cZAn>XQk6n!@l**&#LL$}tVG7Fcf8wOz}bW}J^(oo0jGgz8j8Bh!>d@pDrjJGq>{9Snibu8TyDu(tqQH8iZW76-q1ZED=!yhtZf)Eb(vFkC_gPToIEXx?(Lyf7dNU#*@e5!+)S1l-x7EjZAamBmEl)sT`^IFHqo+8evb>-4b6%bYeX>VYD5hiR7`nL&14%VdXDQylx-k*x;%^Oy8@K^vI}(qeBAFV%h6ELmLldg!7O_ERf#B><pjNkm2+H<$Og=AF(~}u!7>tKgqhn$2GIPMt-`BR>pZdVX|TOggf{_GGptps_$cMvf_sCBm(eRFtE2}_jRKC5+p87@+FC~H%!$s3e1n$iz)?_M3jTnGTFqlbev!nUMCv>TZ(-JwOaUcZ|GGHO5>J-qin3{L&cuOhFbmX+vQj46;!bpS@N?l9?l)WQ{BZs8W9W-K{ohQ`eET6Y<ab}1xWA7db+!#Qq<!ErTt{jfY0rMl_Q+Dy3h=ELXc(U1wzac|7id}G;k8vqYSkPvqS1^sW<bD*wpvoKk3*4Ed@a<I5MNAbXEf%Xad2~QfQMO9bCHTkm0V_q1ZmlJd8d)gnU)RCm~n#Z#c%zLTb&Gi?p`G;{GJ@~l37k(-JV!T{0-eVaIw$K4C}>cHi2!>S~BEp%zF#{2J(*ZcC}s$H!$lgF`=v%@BX%ZYi>6Tf2C*`_Pi7rYPD<Du)y1nwhz&Fim#Nq8Ll+zrTbXT-R+0$1<@x&hi8q7+*SM^RGNxxv3x8DMAx1eOrDPnM*2$HQC>{U=<4&_PE+ff+1`CZ9%f%w<1gEJf0Ng4Jd(|QI5rRe3!QmfDg')).decode('utf-8'))
_ACTIONS = _ACTIONS_8C6S_3Q
__version__ = 'Codex-Moon-V113-V107WeedPostplantWater'

_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25
_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "hinge", 1.0, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "hinge", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "hinge", 0.4, "log", 0.2),
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
_WEED_REPLAY_STEPS = 8
_SHIFT_STATE = {
    0: {"last_step": -1, "debts": {}},
    1: {"last_step": -1, "debts": {}},
}
_PREEMPT_ENABLED = True
_PREEMPT_FRACTION = 1.0
_PREEMPT_MAX_BATCH = 10
_PREEMPT_MAX_CLONE_DISTANCE = 2
_PREEMPT_MIN_PRICE_RATIO = 0.0
_PREEMPT_MIN_FUTURE_QUANTITY = 4
_PREEMPT_START = 160
_PREEMPT_STOP = 700
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")
_ADAPT_MAX_OPP_HORIZON = 3
_ADAPT_MIN_EVIDENCE = 2.0
_ADAPT_DECAY = 0.999
_RACE_STATE = {0: {}, 1: {}}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)



_KAWA_MILK_SUPPORT = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}


def _kawa_route_label(obs):
    shops = list(((_get(obs, "town", {}) or {}).get("unlocked_shops", []) or []))
    if shops[:1] == ["YARN_STORE"]:
        return "6c12s_4q_first_yarn"
    if "YARN_STORE" in shops[:2]:
        return "6c12s_4q_second_yarn"
    if "YARN_STORE" in shops[:3]:
        return "6c8s_3q"
    if _KAWA_MILK_SUPPORT.intersection(shops[:3]):
        return "10c4s_3q"
    return "8c6s_3q"


_KAWA_LAYOUT_FALLBACK = {0: None, 1: None}


def _kawa_use_legacy_layout(obs):
    step = int(_get(obs, "step", 0) or 0)
    seat = _seat(obs)
    if step == 0:
        _KAWA_LAYOUT_FALLBACK[seat] = None
    decision = _KAWA_LAYOUT_FALLBACK.get(seat)
    if decision is None and 24 <= step < 72:
        farms = list(_get(obs, "farms", []) or [])
        opponent = farms[1 - seat] if len(farms) >= 2 else {}
        counts = {"WHEAT": 0, "MELON": 0, "COW": 0, "SHEEP": 0, "PASTURE": 0}
        for row in list(_get(opponent, "tiles", []) or []):
            for tile in list(row or []):
                if not isinstance(tile, dict):
                    continue
                key = tile.get("crop") or tile.get("animal")
                if key in counts:
                    counts[key] += 1
                if tile.get("kind") == "PASTURE" and not tile.get("animal"):
                    counts["PASTURE"] += 1
        decision = (
            counts == {"WHEAT": 5, "MELON": 5, "COW": 1, "SHEEP": 4, "PASTURE": 0}
            and float(_get(opponent, "money", 0) or 0) <= 12
        )
        _KAWA_LAYOUT_FALLBACK[seat] = decision
    return bool(decision)


def _kawa_actions(obs):
    current = {
        "10c4s_3q": _ACTIONS_10C4S_3Q,
        "8c6s_3q": _ACTIONS_8C6S_3Q,
        "6c8s_3q": _ACTIONS_6C8S_3Q,
        "6c12s_4q_first_yarn": _ACTIONS_6C12S_4Q_FIRST_YARN,
        "6c12s_4q_second_yarn": _ACTIONS_6C12S_4Q_SECOND_YARN,
    }
    label = _kawa_route_label(obs)
    if _kawa_use_legacy_layout(obs):
        return {
            "10c4s_3q": _LEGACY_ACTIONS_10C4S_3Q,
            "8c6s_3q": _LEGACY_ACTIONS_8C6S_3Q,
            "6c8s_3q": _LEGACY_ACTIONS_6C8S_3Q,
            "6c12s_4q_first_yarn": _LEGACY_ACTIONS_6C12S_4Q_FIRST_YARN,
            "6c12s_4q_second_yarn": _LEGACY_ACTIONS_6C12S_4Q_SECOND_YARN,
        }[label]
    return current[label]

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


def _planned_premium(obs, step, item):
    actions = _kawa_actions(obs)
    if not (0 <= step < len(actions)):
        return 0
    return sum(
        max(0, int(order[2]))
        for order in (actions[step].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _town_drain(step, shops, item):
    drain = 0
    if step % 4 == 0:
        for shop in shops or ():
            products = _SHOP_PRODUCTS.get(shop, ())
            if item in products:
                drain += 2 if len(products) == 1 else 1
    if step % 24 == 0:
        drain += 1
    return drain


def _race_state(obs, step):
    seat = _seat(obs)
    state = _RACE_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {
            "last_step": -1,
            "inventory": {},
            "prices": {},
            "own_sells": {},
            "shops": (),
            "scores": {
                item: {h: 0.0 for h in range(1, _ADAPT_MAX_OPP_HORIZON + 1)}
                for item in _PREMIUM
            },
            "evidence": {item: 0.0 for item in _PREMIUM},
            "horizon": {item: 1 for item in _PREMIUM},
            "policy_scores": {
                h: 0.0 for h in range(1, _ADAPT_MAX_OPP_HORIZON + 1)
            },
            "policy_evidence": 0.0,
            "policy_horizon": 1,
            "policy_adapt_step": -1,
            "adapted_shifts": 0,
            "adapted_units": 0,
        }
        _RACE_STATE[seat] = state
    return state


def _observe_opponent_market(obs, step):
    state = _race_state(obs, step)
    current_market = _get(obs, "market", {}) or {}
    current = dict(_get(current_market, "inventory", {}) or {})
    current_prices = dict(_get(current_market, "prices", {}) or {})
    previous = dict(state.get("inventory", {}) or {})
    previous_prices = dict(state.get("prices", {}) or {})
    prev_step = int(state.get("last_step", -1))
    state["policy_evidence"] *= _ADAPT_DECAY
    for horizon in state["policy_scores"]:
        state["policy_scores"][horizon] *= _ADAPT_DECAY
    for item in _PREMIUM:
        state["evidence"][item] *= _ADAPT_DECAY
        for horizon in state["scores"][item]:
            state["scores"][item][horizon] *= _ADAPT_DECAY
    if previous and prev_step == step - 1:
        own = dict(state.get("own_sells", {}) or {})
        shops = tuple(state.get("shops", ()) or ())
        for item in _PREMIUM:
            if float(previous_prices.get(item, 2) or 0) <= 1 or float(current_prices.get(item, 2) or 0) <= 1:
                continue
            delta = int(current.get(item, 0) or 0) - int(previous.get(item, 0) or 0)
            opponent_supply = delta + _town_drain(prev_step, shops, item) - int(own.get(item, 0) or 0)
            extra_supply = opponent_supply - _planned_premium(obs, prev_step, item)
            if extra_supply < _PREEMPT_MIN_FUTURE_QUANTITY:
                continue
            state["evidence"][item] += 1.0
            state["policy_evidence"] += 1.0
            for horizon in range(1, _ADAPT_MAX_OPP_HORIZON + 1):
                expected = _planned_premium(obs, prev_step + horizon, item)
                if expected > 0:
                    similarity = min(extra_supply, expected) / float(max(extra_supply, expected))
                    state["scores"][item][horizon] += 1.0 + similarity
                    state["policy_scores"][horizon] += 1.0 + similarity
                else:
                    state["scores"][item][horizon] -= 0.15
                    state["policy_scores"][horizon] -= 0.15
            if state["evidence"][item] >= _ADAPT_MIN_EVIDENCE:
                ranked = sorted(
                    state["scores"][item],
                    key=lambda h: (state["scores"][item][h], -h),
                    reverse=True,
                )
                best = ranked[0]
                runner = state["scores"][item][ranked[1]] if len(ranked) > 1 else -1e9
                if state["scores"][item][best] >= runner + 0.25:
                    state["horizon"][item] = min(_ADAPT_MAX_OPP_HORIZON, best + 1)
    if state["policy_evidence"] >= _ADAPT_MIN_EVIDENCE:
        ranked = sorted(
            state["policy_scores"],
            key=lambda h: (state["policy_scores"][h], -h),
            reverse=True,
        )
        best = ranked[0]
        runner = state["policy_scores"][ranked[1]] if len(ranked) > 1 else -1e9
        if state["policy_scores"][best] >= runner + 0.25:
            if state["policy_horizon"] == 1:
                state["policy_adapt_step"] = step
            state["policy_horizon"] = min(_ADAPT_MAX_OPP_HORIZON, best + 1)
            for item in _PREMIUM:
                if state["horizon"][item] == 1:
                    state["horizon"][item] = state["policy_horizon"]
    state["last_step"] = step
    state["inventory"] = current
    state["prices"] = current_prices
    state["shops"] = tuple(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])


def _record_own_sells(obs, action, step):
    state = _race_state(obs, step)
    remaining = _projected_shed(obs, action)
    sold = {}
    for order in action.get("market", []) or []:
        if len(order) < 3 or order[0] != "SELL" or order[1] not in _PREMIUM:
            continue
        item = order[1]
        quantity = min(max(0, int(order[2])), max(0, int(remaining.get(item, 0) or 0)))
        if quantity:
            sold[item] = sold.get(item, 0) + quantity
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - quantity)
    state["own_sells"] = sold


def _adaptive_horizon(obs, step, item):
    return int(_race_state(obs, step).get("horizon", {}).get(item, 1))


def _shift_state(obs, step):
    seat = _seat(obs)
    state = _SHIFT_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "debts": {}}
        _SHIFT_STATE[seat] = state
    state["last_step"] = step
    return state


def _repay_shift(obs, action, step):
    if not _PREEMPT_ENABLED:
        return action
    state = _shift_state(obs, step)
    debts = state.setdefault("debts", {})
    due = {
        item: max(0, int(quantity))
        for item, quantity in dict(debts.pop(step, {}) or {}).items()
    }
    if not due:
        return action
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
    return action


def _preempt_shift(obs, action, step):
    if not _PREEMPT_ENABLED or not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    state = _shift_state(obs, step)
    race = _race_state(obs, step)
    clone_like = _clone_distance(obs) <= _PREEMPT_MAX_CLONE_DISTANCE
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            item = raw[1]
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    choices = []
    for item in _PREMIUM:
        if not clone_like and max(
            float(race.get("evidence", {}).get(item, 0.0) or 0.0),
            float(race.get("policy_evidence", 0.0) or 0.0),
        ) < _ADAPT_MIN_EVIDENCE:
            continue
        base_price = float(_MARKET_PARAMS[item][0])
        if float(_get(prices, item, 0) or 0) < base_price * _PREEMPT_MIN_PRICE_RATIO:
            continue
        preferred = _adaptive_horizon(obs, step, item)
        # Try the inferred second-order lead first, then back off to the
        # farthest lead for which inventory is actually in the shed.  Horizon
        # one is the exact V17 fallback.
        for horizon in range(preferred, 0, -1):
            future_quantity = _planned_premium(obs, step + horizon, item)
            if future_quantity < _PREEMPT_MIN_FUTURE_QUANTITY:
                continue
            target = min(
                max(0, int(remaining.get(item, 0) or 0)),
                future_quantity,
                _PREEMPT_MAX_BATCH,
                max(1, int(round(future_quantity * _PREEMPT_FRACTION))),
            )
            if target > 0:
                choices.append(
                    (float(_get(prices, item, 0) or 0) * target, item, target, horizon)
                )
                break
    # Preserve V17's behavior before inference.  Once a product is evidence-
    # adapted, shift only the highest-value adapted opportunity this turn.
    adapted = [choice for choice in choices if choice[3] > 1]
    selected = [max(adapted)] if adapted else (choices if clone_like else [])
    if adapted and selected:
        race = _race_state(obs, step)
        race["adapted_shifts"] = int(race.get("adapted_shifts", 0)) + 1
        race["adapted_units"] = int(race.get("adapted_units", 0)) + int(selected[0][2])
    for _, item, target, horizon in selected:
        if len(market) >= 10:
            break
        market.append(["SELL", item, target])
        remaining[item] = max(0, int(remaining.get(item, 0) or 0) - target)
        debts = state.setdefault("debts", {})
        due = debts.setdefault(step + horizon, {})
        due[item] = due.get(item, 0) + target
    if selected:
        action["market"] = market[:10]
    return action


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(obs, step, actor):
    actions = _kawa_actions(obs)
    trace = actions[min(max(int(step), 0), len(actions) - 1)] or {}
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
            replayed = _trace_actor_action(obs, step - 1, actor)
            # If a delayed PLANT landed after another actor's same-turn WATER,
            # the crop is still dry.  Use only an inherited idle slot to water
            # it; never displace movement or productive work.
            intended = list(transaction.get("intended") or [])
            tile = _tile_at(farm, positions[index]) if index < len(positions) else None
            if (
                age == 2
                and replayed == ["PASS"]
                and len(intended) >= 2
                and intended[0] == "PLANT"
                and isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == intended[1]
                and not bool(tile.get("watered_today", False))
            ):
                replayed = ["WATER"]
            unit_actions[index] = replayed
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
_V17_R5_FRACTION = 0.5
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
    future = step + 3
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


def _shape(name, value, scale=None):
    value = max(0.0, float(value))
    if name == "hinge":
        if scale is None or float(scale) <= 0:
            raise ValueError("hinge requires a positive scale")
        u = value / float(scale)
        return u + 8.0 * max(0.0, u - 1.0) ** 2
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
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
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


def _v20_move_toward(position, target, tiles):
    x, y = int(position[0]), int(position[1])
    tx, ty = int(target[0]), int(target[1])
    choices = []
    if tx < x:
        choices.append(("WEST", (x - 1, y)))
    if tx > x:
        choices.append(("EAST", (x + 1, y)))
    if ty < y:
        choices.append(("NORTH", (x, y - 1)))
    if ty > y:
        choices.append(("SOUTH", (x, y + 1)))
    size = len(tiles)
    for operation, (nx, ny) in choices:
        if 0 <= nx < size and 0 <= ny < size and tiles[ny][nx] != "LOCKED":
            return [operation]
    return ["PASS"]


def _v20_terminal_action(obs):
    seat = _seat(obs)
    farm = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    tiles = list(_get(farm, "tiles", []) or [])
    size = len(tiles)
    positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    inventories = list(_get(private, "inventories", []) or [])
    inventories.extend({} for _ in range(len(positions) - len(inventories)))
    sheds = set(_shed_access(size))
    available = {
        (x, y)
        for y, row in enumerate(tiles)
        for x, tile in enumerate(row)
        if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0
    }
    actions = []
    pending = {}
    for raw_position, inventory in zip(positions, inventories):
        position = tuple(raw_position)
        inventory = inventory or {}
        load = sum(max(0, int(value or 0)) for value in inventory.values())
        x, y = position
        tile = tiles[y][x] if 0 <= y < size and 0 <= x < size else None
        if load > 0 and position in sheds:
            unit_action = ["DROP"]
            for item, count in inventory.items():
                if item in _SELLABLE:
                    pending[item] = pending.get(item, 0) + max(0, int(count or 0))
        elif isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0:
            unit_action = ["HARVEST"]
            available.discard(position)
        elif load > 0:
            target = min(sheds, key=lambda cell: abs(cell[0] - x) + abs(cell[1] - y))
            unit_action = _v20_move_toward(position, target, tiles)
        elif available:
            target = min(
                available,
                key=lambda cell: (abs(cell[0] - x) + abs(cell[1] - y), cell[1], cell[0]),
            )
            available.discard(target)
            unit_action = _v20_move_toward(position, target, tiles)
        elif isinstance(tile, dict) and tile.get("fertilizer_available", False):
            unit_action = ["COLLECT_FERTILIZER"]
        else:
            unit_action = ["PASS"]
        actions.append(unit_action)
    shed = dict(_get(private, "shed", {}) or {})
    for item, count in pending.items():
        shed[item] = int(shed.get(item, 0) or 0) + count
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    sells = [
        (int(shed.get(item, 0) or 0) * int(_get(prices, item, 1) or 1), item,
         int(shed.get(item, 0) or 0))
        for item in _SELLABLE
        if int(shed.get(item, 0) or 0) > 0
    ]
    sells.sort(reverse=True)
    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": [["SELL", item, quantity] for _, item, quantity in sells[:10]],
    }


_V38_TOMATO_TARGET = 3
_V38_TOMATO_STATE = {
    0: {"last_step": -1, "active": False, "scheduled_plants": 0},
    1: {"last_step": -1, "active": False, "scheduled_plants": 0},
}


def _v38_farm_pair_tomatoes(obs, action, step):
    """Convert a prefix-aligned part of the day-11 strawberry cohort."""
    seat = _seat(obs)
    state = _V38_TOMATO_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "active": False, "scheduled_plants": 0}
        _V38_TOMATO_STATE[seat] = state
    state["last_step"] = step
    if step == 216:
        shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])[:3]
        state["active"] = sum(
            shop in ("FARMERS_MARKET", "PIZZA_SHOP") for shop in shops
        ) >= 2
    if not state.get("active"):
        return action

    action = _copy_action(action)
    market = list(action.get("market") or [])
    if step == 264:
        strawberry_buy = next(
            (
                order
                for order in market
                if isinstance(order, list)
                and len(order) >= 3
                and order[:2] == ["BUY_SEED", "STRAWBERRY"]
                and int(order[2] or 0) >= _V38_TOMATO_TARGET
            ),
            None,
        )
        if strawberry_buy is not None:
            strawberry_buy[2] = int(strawberry_buy[2] or 0) - _V38_TOMATO_TARGET
            state["seed_debt"] = _V38_TOMATO_TARGET
    if step == 265 and int(state.get("seed_debt", 0) or 0) > 0 and len(market) < 10:
        market.append(["BUY_SEED", "TOMATO", int(state["seed_debt"])])
        state["seed_debt"] = 0

    private = _get(obs, "private", {}) or {}
    inventories = [dict(value or {}) for value in list(_get(private, "inventories", []) or [])]
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    if 271 <= step <= 286:
        remaining = max(0, _V38_TOMATO_TARGET - int(state.get("scheduled_plants", 0)))
        changed = 0
        for order in orders:
            if (
                changed < remaining
                and isinstance(order, list)
                and len(order) >= 2
                and order[:2] == ["PLANT", "STRAWBERRY"]
            ):
                order[1] = "TOMATO"
                changed += 1
        state["scheduled_plants"] = int(state.get("scheduled_plants", 0)) + changed
    for actor, order in enumerate(orders):
        if (
            actor < len(inventories)
            and isinstance(order, list)
            and len(order) >= 2
            and order[:2] == ["PLACE", "STRAWBERRY"]
            and int(inventories[actor].get("TOMATO", 0) or 0) > 0
        ):
            order[1] = "TOMATO"
    action["farmer"] = orders[0]
    action["hands"] = orders[1:]

    if step >= 432 and step % 24 == 0:
        shed = dict(_get(private, "shed", {}) or {})
        tomatoes = max(0, int(shed.get("TOMATO", 0) or 0))
        existing = next(
            (
                order
                for order in market
                if isinstance(order, list)
                and len(order) >= 3
                and order[:2] == ["SELL", "TOMATO"]
            ),
            None,
        )
        if tomatoes and existing is not None:
            existing[2] = max(int(existing[2] or 0), tomatoes)
        elif tomatoes and len(market) < 10:
            market.append(["SELL", "TOMATO", tomatoes])
    # Let the scarcity patch compound before monetizing this small cohort.
    # The terminal controller at step 708 sees the held shed stock and liquidates it.
    market = [
        order
        for order in market
        if not (
            isinstance(order, list)
            and len(order) >= 2
            and order[:2] == ["SELL", "TOMATO"]
        )
    ]
    action["market"] = market[:10]
    return action


# Ryo's public route begins relaying carrots after its fifth shop, while
# Subramanya's largest public carrot cohort uses the ordinary crop relays.
# V58 has both physical seams.  Safe early wheat plots receive one mature
# watering and a later inherited WATER visit before carrot expiry; that later
# visit can harvest the carrot without changing movement.  The step-613..622
# terminal wheat cohort already has inherited water and harvest orders.  Both
# replacements therefore need no new worker, movement, or route overlay.
_V71_CARROT_TARGET = 12
_V71_CARROT_START = 613
_V71_CARROT_STOP = 622
_V71_EARLY_EXPECTED_UNITS = 0
_V71_EARLY_MIN_STEP = 589
_V71_EARLY_MAX_STEP = 610
_V71_EARLY_QUOTE_GATE = 110
# These are inherited V58 plant slots whose routes revisit the same plot for
# one mature watering and then again before carrot max_lifespan_step.  The set
# covers both public layout branches; a slot is used only when the live action
# is actually PLANT WHEAT.
_V71_EARLY_SLOTS = {
    # Normal layout, first relay.
    (541, 7), (545, 10), (546, 11), (547, 0),
    (547, 4), (548, 2), (549, 7), (549, 11),
    # Legacy/public Wufang layout, first relay.
    (541, 10), (542, 7), (543, 11), (545, 12),
    # Normal layout, second relay.
    (569, 7), (569, 10), (571, 5), (573, 6),
    # Legacy/public Wufang layout, second relay.
    (565, 7), (570, 7), (571, 1), (572, 0), (572, 5),
    (572, 9), (573, 3), (574, 8),
    # Normal layout, third relay.
    (589, 9), (594, 11), (595, 2), (595, 8), (595, 9),
    (597, 6), (598, 2), (598, 9),
    # Legacy/public Wufang layout, third relay.
    (594, 7), (598, 11), (610, 11),
}
_V71_POST_EXPECTED_UNITS = 36
# Final inherited wheat plants whose ordinary harvest lands no later than
# step 707.  Carrot and wheat both realize two units on these routes, but the
# former is worth materially more under the confirmed scarcity gate.  Crops
# with a source harvest at 708+ are deliberately excluded because V58's
# terminal controller takes over then.
_V71_POST_SLOTS = {
    # Normal layout.
    (636, 11), (640, 8), (641, 7), (643, 0), (643, 4),
    (643, 5), (643, 8), (645, 2), (646, 0), (655, 7),
    (659, 10), (665, 11), (666, 0), (666, 6), (668, 3),
    (669, 0), (669, 4), (670, 10),
    # Legacy/public Wufang layout.
    (639, 2), (641, 1), (642, 11), (645, 0), (645, 10),
    (664, 2), (664, 5), (665, 6), (666, 0), (666, 11),
    (667, 1), (668, 4), (668, 5), (670, 2), (670, 6),
}
_V71_BASE_CARROT_UNITS = 11
_V71_EXPECTED_YIELD = 3
_V71_CARROT_STATE = {
    0: {
        "last_step": -1,
        "preliminary": False,
        "active": False,
        "early_active": False,
        "decision_quote": 0,
        "plants": 0,
        "post_plants": 0,
        "seed_debt": 0,
        "lost_wheat": 0,
        "early_tiles": {},
    },
    1: {
        "last_step": -1,
        "preliminary": False,
        "active": False,
        "early_active": False,
        "decision_quote": 0,
        "plants": 0,
        "post_plants": 0,
        "seed_debt": 0,
        "lost_wheat": 0,
        "early_tiles": {},
    },
}


def _v71_live_units(farm, crop):
    units = 0
    for row in list(_get(farm, "tiles", []) or []):
        for tile in list(row or []):
            if (
                isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == crop
            ):
                units += max(1, int(tile.get("yield_units", 0) or 0))
    return units


def _v71_animal_count(farm):
    return sum(
        1
        for row in list(_get(farm, "tiles", []) or [])
        for tile in list(row or [])
        if isinstance(tile, dict) and tile.get("animal")
    )


def _v71_carrot_decision(obs, target_units):
    """Public demand/deficit gate with a conservative replacement NPV."""
    step = int(_get(obs, "step", 0) or 0)
    shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])
    shops = shops[: max(3, len(shops))]
    carrot_shop_score = sum(
        2 if shop == "PET_CAFE" else 1 if shop == "FARMERS_MARKET" else 0
        for shop in shops
    )
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    carrot_inventory = int(_get(inventory, "CARROT", 10000) or 10000)
    remaining_demand = sum(
        _town_drain(future, shops, "CARROT")
        for future in range(step, 720)
    )
    # The eight shops unlock deterministically every three days, but their
    # identities remain random.  A future shop consumes an expected 3/8 of a
    # carrot per town tick: PET_CAFE contributes 2/8 and FARMERS_MARKET 1/8.
    # This is distributional demand, not a seed or shop-sequence lookup.
    for shop_number in range(len(shops) + 1, 9):
        unlock_step = 72 * shop_number
        ticks = sum(
            1
            for future in range(max(step, unlock_step), 720)
            if future % 4 == 0
        )
        remaining_demand += (3.0 / 8.0) * ticks
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    # A visible live opponent carrot is valued at its full four-unit capacity.
    opponent_carrots = sum(
        1
        for row in list(_get(opponent, "tiles", []) or [])
        for tile in list(row or [])
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "CARROT"
        )
    )
    opponent_capacity = 4 * opponent_carrots
    opponent_strawberries = sum(
        1
        for row in list(_get(opponent, "tiles", []) or [])
        for tile in list(row or [])
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "STRAWBERRY"
        )
    )
    opponent_animals = _v71_animal_count(opponent)
    # At the confirmation step, preserve the incumbent route against visibly
    # lower-throughput animal-heavy farms.  A live carrot cohort or a dense
    # strawberry surface is direct evidence that the rival can contest the
    # same late crop route; compact <=12-animal layouts are the other public
    # high-throughput shape in the replay set.
    rival_route_ready = bool(
        step < 288
        or opponent_carrots > 0
        or opponent_strawberries >= 36
        or opponent_animals <= 12
    )
    projected_inventory = (
        carrot_inventory
        - remaining_demand
        + opponent_capacity
        + _V71_BASE_CARROT_UNITS
        + max(0, int(target_units))
    )
    carrot_quote = _market_price("CARROT", projected_inventory)
    _V71_CARROT_STATE[seat]["decision_quote"] = carrot_quote
    wheat_quote = int(_get(prices, "WHEAT", 25) or 25)
    replacement_npv = (
        _V71_EXPECTED_YIELD * (carrot_quote - wheat_quote)
        - 10  # carrot seed costs ten more than the replaced wheat seed
    )
    return bool(
        carrot_shop_score >= 3
        and rival_route_ready
        and carrot_inventory < 9975
        and projected_inventory <= 9575
        and replacement_npv >= 20
    )


def _v71_pair_seed_debt(action, state):
    """Replace matching wheat seed replenishment without adding order pressure."""
    debt = max(0, int(state.get("seed_debt", 0) or 0))
    if debt <= 0:
        return action
    market = list(action.get("market") or [])
    for order in market:
        if debt <= 0:
            break
        if not (
            isinstance(order, list)
            and len(order) >= 3
            and order[:2] == ["BUY_SEED", "WHEAT"]
        ):
            continue
        quantity = max(0, int(order[2] or 0))
        # Cohort steps buy exactly as many wheat seeds as they plant.  Only an
        # exact prefix is relabeled, so this stays one market order.
        transfer = min(debt, quantity)
        if transfer == quantity:
            order[1] = "CARROT"
            debt -= transfer
        elif len(market) < 10:
            order[2] = quantity - transfer
            market.append(["BUY_SEED", "CARROT", transfer])
            debt -= transfer
    state["seed_debt"] = debt
    action["market"] = market[:10]
    return action


def _v71_route_carrots(obs, action, step):
    """Relabel complete inherited wheat cohorts after two public decisions."""
    seat = _seat(obs)
    state = _V71_CARROT_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {
            "last_step": step,
            "preliminary": False,
            "active": False,
            "early_active": False,
            "decision_quote": 0,
            "plants": 0,
            "post_plants": 0,
            "seed_debt": 0,
            "lost_wheat": 0,
            "early_tiles": {},
        }
        _V71_CARROT_STATE[seat] = state
    state["last_step"] = step

    target_units = (
        _V71_CARROT_TARGET * _V71_EXPECTED_YIELD
        + _V71_EARLY_EXPECTED_UNITS
        + _V71_POST_EXPECTED_UNITS
    )
    if step == 216:
        state["preliminary"] = _v71_carrot_decision(obs, target_units)
    if step == 288:
        state["active"] = bool(
            state.get("preliminary")
            and _v71_carrot_decision(obs, target_units)
        )
        # A small third relay is worthwhile only in the genuinely scarce
        # tail.  This uses the same observation-derived projected quote as the
        # main NPV gate; it is not tied to an opponent, seed, or shop tape.
        state["early_active"] = bool(
            state.get("active")
            and int(state.get("decision_quote", 0) or 0)
            >= _V71_EARLY_QUOTE_GATE
        )
    if not state.get("active"):
        return action

    action = _copy_action(action)
    private = _get(obs, "private", {}) or {}
    farm = _farm(obs, seat)
    inventories = list(_get(private, "inventories", []) or [])
    wheat_stock = int(_get(_get(private, "shed", {}) or {}, "WHEAT", 0) or 0)
    wheat_stock += sum(
        max(0, int(_get(inventory, "WHEAT", 0) or 0))
        for inventory in inventories
    )
    live_wheat = _v71_live_units(farm, "WHEAT")
    feed_reserve = 2 * _v71_animal_count(farm)
    # live_wheat is read from the *current* board, so previously converted
    # plots have already disappeared from it.  Subtracting lost_wheat again
    # would double-count the replacement and unnecessarily clip later plants.
    available_wheat = wheat_stock + live_wheat

    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    positions = [
        _get(farm, "farmer", [4, 4]),
        *list(_get(farm, "hands", []) or []),
    ]
    early_tiles = state.setdefault("early_tiles", {})

    # Drop a tracked plot only after the PLANT action has had a turn to become
    # visible.  This also makes failed plant attempts self-healing instead of
    # causing unrelated future route visits to be rewritten.
    for position, record in list(early_tiles.items()):
        tile = _tile_at(farm, position)
        if (
            step > int(record.get("plant_step", step) or step) + 1
            and not (
                isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == "CARROT"
            )
        ):
            early_tiles.pop(position, None)

    # The whitelist is a mechanical property of the inherited route, not an
    # opponent or seed lookup.  A slot is converted only when the live action
    # remains PLANT WHEAT and the visible wheat supply still covers two units
    # of feed per animal.
    early_changed = 0
    for actor, (order, position) in enumerate(zip(orders, positions)):
        if not state.get("early_active"):
            continue
        if not (_V71_EARLY_MIN_STEP <= step <= _V71_EARLY_MAX_STEP):
            continue
        if (step, actor) not in _V71_EARLY_SLOTS:
            continue
        if available_wheat - _V71_EXPECTED_YIELD < feed_reserve:
            break
        if not (
            isinstance(order, list)
            and len(order) >= 2
            and order[:2] == ["PLANT", "WHEAT"]
        ):
            continue
        order[1] = "CARROT"
        key = (int(position[0]), int(position[1]))
        early_tiles[key] = {
            "plant_step": step,
            "mature_watered": False,
        }
        early_changed += 1
        available_wheat -= _V71_EXPECTED_YIELD

    if early_changed:
        state["seed_debt"] = int(state.get("seed_debt", 0) or 0) + early_changed
        state["lost_wheat"] = int(state.get("lost_wheat", 0) or 0) + (
            early_changed * _V71_EXPECTED_YIELD
        )

    # Carrots mature one day sooner than the inherited wheat.  Keep the first
    # mature WATER (raising the crop to two units at end of day), then turn the
    # next already-routed WATER on that tile into HARVEST.  All whitelisted
    # plots have this second visit before max_lifespan_step.
    day = int(_get(obs, "day", step // 24) or 0)
    for actor, (order, position) in enumerate(zip(orders, positions)):
        key = (int(position[0]), int(position[1]))
        record = early_tiles.get(key)
        if record is None or not isinstance(order, list) or not order:
            continue
        tile = _tile_at(farm, position)
        if not (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "CARROT"
        ):
            continue
        if order[0] == "HARVEST":
            early_tiles.pop(key, None)
            continue
        if order[0] != "WATER":
            continue
        planted_day = int(tile.get("planted_day", day) or day)
        if day < planted_day + 2:
            continue
        if record.get("mature_watered"):
            order[:] = ["HARVEST"]
            early_tiles.pop(key, None)
        else:
            record["mature_watered"] = True

    if early_changed:
        action["farmer"] = orders[0]
        action["hands"] = orders[1:]

    if _V71_CARROT_START <= step <= _V71_CARROT_STOP:
        remaining = max(0, _V71_CARROT_TARGET - int(state.get("plants", 0) or 0))
        changed = 0
        for order in orders:
            if changed >= remaining:
                break
            if available_wheat - _V71_EXPECTED_YIELD < feed_reserve:
                break
            if (
                isinstance(order, list)
                and len(order) >= 2
                and order[:2] == ["PLANT", "WHEAT"]
            ):
                order[1] = "CARROT"
                changed += 1
                available_wheat -= _V71_EXPECTED_YIELD
        if changed:
            state["plants"] = int(state.get("plants", 0) or 0) + changed
            state["seed_debt"] = int(state.get("seed_debt", 0) or 0) + changed
            state["lost_wheat"] = int(state.get("lost_wheat", 0) or 0) + (
                changed * _V71_EXPECTED_YIELD
            )
            action["farmer"] = orders[0]
            action["hands"] = orders[1:]

    # The second route-aligned cohort is closer to game end: its inherited
    # harvest already occurs within carrot lifespan, so only PLANT relabeling
    # and paired seed replenishment are required.
    post_changed = 0
    for actor, order in enumerate(orders):
        if (step, actor) not in _V71_POST_SLOTS:
            continue
        if available_wheat - 2 < feed_reserve:
            break
        if not (
            isinstance(order, list)
            and len(order) >= 2
            and order[:2] == ["PLANT", "WHEAT"]
        ):
            continue
        order[1] = "CARROT"
        post_changed += 1
        available_wheat -= 2
    if post_changed:
        state["post_plants"] = int(state.get("post_plants", 0) or 0) + post_changed
        state["seed_debt"] = int(state.get("seed_debt", 0) or 0) + post_changed
        state["lost_wheat"] = int(state.get("lost_wheat", 0) or 0) + (
            post_changed * 2
        )

    # A rewritten early harvest changes the shared order objects even when no
    # plant occurred this turn, so always write the aligned actor arrays back.
    action["farmer"] = orders[0]
    action["hands"] = orders[1:]

    action = _v71_pair_seed_debt(action, state)

    # Sell completed early cohorts on the next day boundary so they do not
    # occupy the shed until the terminal route.  Expand an inherited carrot
    # sale in place; otherwise use one free market slot.  The market cap is
    # never exceeded, and the terminal controller still liquidates at 708.
    shed_carrots = max(
        0,
        int(_get(_get(private, "shed", {}) or {}, "CARROT", 0) or 0),
    )
    market = list(action.get("market") or [])
    carrot_sale = next(
        (
            order
            for order in market
            if isinstance(order, list)
            and len(order) >= 3
            and order[:2] == ["SELL", "CARROT"]
        ),
        None,
    )
    if shed_carrots and carrot_sale is not None:
        carrot_sale[2] = max(int(carrot_sale[2] or 0), shed_carrots)
    elif shed_carrots and step % 24 == 0 and len(market) < 10:
        market.append(["SELL", "CARROT", shed_carrots])
    action["market"] = market[:10]
    return action


# V58 plants this final seven-plot strawberry relay immediately after the
# fourth public shop. Each plot already has inherited WATER, FERTILIZE, and
# HARVEST visits through the tomato horizon, so no actor or movement is added.
_V73_TOMATO_TARGET = 7
_V73_TOMATO_UNITS = 35
_V73_LOST_STRAWBERRY_UNITS = 42
_V73_ROUTE_RESERVE = 500
_V73_ROUTE_SLOTS = {
    (297, 7), (300, 7), (303, 7), (304, 8),
    (305, 6), (306, 7), (309, 7),
}
_V73_STATE = {
    0: {"last_step": -1, "active": False, "seed_debt": 0, "scheduled": 0, "tiles": {}, "decision": {}},
    1: {"last_step": -1, "active": False, "seed_debt": 0, "scheduled": 0, "tiles": {}, "decision": {}},
}


def _v89_tomato_route_ready(obs, action):
    """Confirm that the live-selected route owns all seven relay slots."""
    actions = _kawa_actions(obs)
    current_actors = 1 + len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    planned_hires = sum(
        1
        for order in (action.get("market") or [])
        if isinstance(order, list) and order[:1] == ["HIRE"]
    )
    planned_hires += sum(
        1
        for future_step in range(289, min(297, len(actions)))
        for order in ((actions[future_step] or {}).get("market") or [])
        if isinstance(order, list) and order[:1] == ["HIRE"]
    )
    available_actors = current_actors + planned_hires
    matched = 0
    for route_step, actor in sorted(_V73_ROUTE_SLOTS):
        if route_step >= len(actions) or actor >= available_actors:
            continue
        raw = actions[route_step] or {}
        orders = [raw.get("farmer", ["PASS"]), *list(raw.get("hands") or [])]
        if (
            actor < len(orders)
            and isinstance(orders[actor], list)
            and orders[actor][:2] == ["PLANT", "STRAWBERRY"]
        ):
            matched += 1
    return {
        "route_slots_ready": matched == _V73_TOMATO_TARGET,
        "route_slots_matched": matched,
        "route_actor_capacity": available_actors,
    }


def _v73_visible_ongoing_supply(farm, crop, day):
    schedule = {
        "TOMATO": (8, 9, 10, 11),
        "STRAWBERRY": (10, 12, 14, 16),
    }.get(crop, ())
    supply = 0
    for row in list(_get(farm, "tiles", []) or []):
        for tile in list(row or []):
            if not (
                isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == crop
            ):
                continue
            supply += max(0, int(tile.get("yield_units", 0) or 0))
            age = day - int(tile.get("planted_day", day) or day)
            supply += 2 * sum(production_age > age for production_age in schedule)
    return supply


def _v73_integrated_value(item, inventory, quantity):
    return sum(
        _market_price(item, inventory + offset)
        for offset in range(max(0, int(quantity)))
    )


def _v73_tomato_decision(obs, step):
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    day = int(_get(obs, "day", step // 24) or 0)
    shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])[:4]
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    tomato_current = int(_get(inventory, "TOMATO", 10000) or 10000)
    strawberry_current = int(_get(inventory, "STRAWBERRY", 10000) or 10000)
    tomato_drain = sum(_town_drain(future, shops, "TOMATO") for future in range(step, 708))
    strawberry_drain = sum(
        _town_drain(future, shops, "STRAWBERRY")
        for future in range(step, 708)
    )
    opponent_tomato = _v73_visible_ongoing_supply(opponent, "TOMATO", day)
    opponent_strawberry = _v73_visible_ongoing_supply(opponent, "STRAWBERRY", day)
    tomato_projected = tomato_current - tomato_drain + opponent_tomato
    strawberry_projected = strawberry_current - strawberry_drain + opponent_strawberry
    tomato_value = _v73_integrated_value("TOMATO", tomato_projected, _V73_TOMATO_UNITS)
    strawberry_value = _v73_integrated_value(
        "STRAWBERRY", strawberry_projected, _V73_LOST_STRAWBERRY_UNITS
    )
    npv = (
        tomato_value
        - strawberry_value
        - 50 * _V73_TOMATO_TARGET
        - _V73_ROUTE_RESERVE
    )
    tomato_shops = sum(
        shop in ("FARMERS_MARKET", "PIZZA_SHOP") for shop in shops
    )
    active = bool(
        len(shops) >= 4
        and tomato_shops >= 2
        and tomato_projected <= 9750
        and npv > 0
    )
    return {
        "active": active,
        "shops": shops,
        "tomato_current": tomato_current,
        "tomato_drain": tomato_drain,
        "opponent_tomato_supply": opponent_tomato,
        "tomato_projected_inventory": tomato_projected,
        "strawberry_current": strawberry_current,
        "strawberry_drain": strawberry_drain,
        "opponent_strawberry_supply": opponent_strawberry,
        "strawberry_projected_inventory": strawberry_projected,
        "tomato_value": tomato_value,
        "strawberry_value": strawberry_value,
        "npv": npv,
    }


def _v73_route_tomatoes(obs, action, step):
    seat = _seat(obs)
    state = _V73_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {
            "last_step": step,
            "active": False,
            "seed_debt": 0,
            "scheduled": 0,
            "tiles": {},
            "decision": {},
        }
        _V73_STATE[seat] = state
    state["last_step"] = step
    if step == 288:
        decision = _v73_tomato_decision(obs, step)
        decision.update(_v89_tomato_route_ready(obs, action))
        state["active"] = bool(
            decision.get("active")
            and decision.get("route_slots_ready")
            and not _V38_TOMATO_STATE.get(seat, {}).get("active", False)
        )
        state["seed_debt"] = _V73_TOMATO_TARGET if state["active"] else 0
        state["decision"] = decision
    if not state.get("active"):
        return action

    action = _copy_action(action)
    market = list(action.get("market") or [])
    debt = max(0, int(state.get("seed_debt", 0) or 0))
    if debt and step < 297 and len(market) < 10:
        market.append(["BUY_SEED", "TOMATO", debt])
        state["seed_debt"] = 0
    action["market"] = market[:10]

    farm = _farm(obs, seat)
    positions = [
        _get(farm, "farmer", [4, 4]),
        *list(_get(farm, "hands", []) or []),
    ]
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tracked = state.setdefault("tiles", {})
    for actor, (order, position) in enumerate(zip(orders, positions)):
        if (
            (step, actor) in _V73_ROUTE_SLOTS
            and state.get("seed_debt", 0) == 0
            and isinstance(order, list)
            and len(order) >= 2
            and order[:2] == ["PLANT", "STRAWBERRY"]
        ):
            order[1] = "TOMATO"
            key = (int(position[0]), int(position[1]))
            tracked[key] = {"plant_step": step}
            state["scheduled"] = int(state.get("scheduled", 0) or 0) + 1

    day = int(_get(obs, "day", step // 24) or 0)
    for order, position in zip(orders, positions):
        if not isinstance(order, list) or not order:
            continue
        key = (int(position[0]), int(position[1]))
        if key not in tracked or order[0] != "WATER":
            continue
        tile = _tile_at(farm, position)
        if not (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "TOMATO"
        ):
            continue
        planted_day = int(tile.get("planted_day", day) or day)
        if day >= planted_day + 11 and int(tile.get("yield_units", 0) or 0) > 0:
            order[:] = ["HARVEST"]
            tracked.pop(key, None)
    action["farmer"] = orders[0]
    action["hands"] = orders[1:]
    return action


def _v79_rival_strawberry_flush(obs, action, step):
    if step < 216:
        return action
    shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])
    if shops[:3] != ["BAKERY", "FARMERS_MARKET", "PET_CAFE"]:
        return action
    actions = _kawa_actions(obs)
    raw = actions[min(max(0, int(step)), len(actions) - 1)]
    planned_now = sum(
        max(0, int(order[2]))
        for order in (raw.get("market") or [])
        if len(order) >= 3 and order[:2] == ["SELL", "STRAWBERRY"]
    )
    if planned_now <= 0:
        return action
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    rival_ready = sum(
        max(0, int(tile.get("yield_units", 0) or 0))
        for row in list(_get(opponent, "tiles", []) or [])
        for tile in list(row or [])
        if isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
        and tile.get("crop") == "STRAWBERRY"
    )
    if rival_ready < 8:
        return action
    action = _copy_action(action)
    market = [list(order) for order in (action.get("market") or [])]
    existing = sum(
        max(0, int(order[2]))
        for order in market
        if len(order) >= 3 and order[:2] == ["SELL", "STRAWBERRY"]
    )
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    available = max(
        0,
        int(_get(shed, "STRAWBERRY", 0) or 0)
        - existing
        - _v17_md_pickup_reserve(action, "STRAWBERRY"),
    )
    quantity = min(20, rival_ready, available)
    if quantity <= 0:
        return action
    inventory = int(
        _get(
            _get(_get(obs, "market", {}) or {}, "inventory", {}) or {},
            "STRAWBERRY",
            10000,
        )
        or 10000
    )
    sell_now = sum(
        _market_price("STRAWBERRY", inventory + existing + offset)
        for offset in range(quantity)
    )
    sell_after_rival = sum(
        _market_price("STRAWBERRY", inventory + rival_ready + existing + offset)
        for offset in range(quantity)
    )
    # Require enough integrated displacement value to cover the opportunity
    # cost of moving this inventory ahead of the inherited sale route.  Tiny
    # batches carry an extra timing-uncertainty reserve because one rival sale
    # can erase their modeled edge before the next inherited sell window.
    uncertainty_reserve = 150 + 100 * max(0, 4 - quantity)
    if sell_now - sell_after_rival < uncertainty_reserve:
        return action
    order = next(
        (
            order
            for order in market
            if len(order) >= 3 and order[:2] == ["SELL", "STRAWBERRY"]
        ),
        None,
    )
    if order is not None:
        order[2] = max(0, int(order[2])) + quantity
    elif len(market) < 10:
        market.append(["SELL", "STRAWBERRY", quantity])
    else:
        return action
    action["market"] = market[:10]
    return action


_V35_EGG_SHOPS = {"BAKERY", "BRUNCH_SPOT"}
_V35_EGG_STATE = {
    0: {"last_step": -1, "active": False},
    1: {"last_step": -1, "active": False},
}


def _v35_opponent_has_goose(obs):
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    for row in list(_get(opponent, "tiles", []) or []):
        for tile in list(row or []):
            if isinstance(tile, dict) and (
                tile.get("kind") == "COOP" or tile.get("animal") == "GOOSE"
            ):
                return True
    return False


def _v35_egg_late_pair(obs, action, step):
    """Turn only the day-11 animal pair into geese in strong egg regimes.

    By day 11 the first three shops are public.  Two early egg shops are a
    deliberately narrow enrichment gate for the patched egg hinge.  The
    existing tape already builds, feeds, visits, and harvests two new animal
    structures on these steps, so the fork changes the complete cohort rather
    than overlaying unrelated goose actions on the route.
    """
    seat = _seat(obs)
    state = _V35_EGG_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "active": False}
        _V35_EGG_STATE[seat] = state
    state["last_step"] = step
    if step == 264:
        shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])[:3]
        egg_shops = sum(shop in _V35_EGG_SHOPS for shop in shops)
        state["active"] = bool(
            egg_shops >= 2
            and "YARN_STORE" not in shops
            and shops != ["BAKERY", "BAKERY", "BAKERY"]
            and shops != ["ICE_CREAM_SHOP", "BAKERY", "BAKERY"]
            and not (
                shops == ["BRUNCH_SPOT", "BRUNCH_SPOT", "FARMERS_MARKET"]
                and _clone_distance(obs) == 0
            )
            and not _v35_opponent_has_goose(obs)
        )
    if not state.get("active"):
        return action

    action = _copy_action(action)
    if 264 <= step <= 275:
        orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        for order in orders:
            if not isinstance(order, list) or not order:
                continue
            if step in (266, 269) and order[0] == "BUILD_PASTURE":
                order[0] = "BUILD_COOP"
            elif (
                267 <= step <= 275
                and order[0] in ("PICKUP", "PLACE")
                and len(order) >= 2
                and order[1] in ("COW", "SHEEP")
            ):
                order[1] = "GOOSE"
        action["farmer"] = orders[0]
        action["hands"] = orders[1:]
        for order in action.get("market", []) or []:
            if (
                step == 264
                and isinstance(order, list)
                and len(order) >= 3
                and order[0] == "BUY_ANIMAL"
                and order[1] in ("COW", "SHEEP")
            ):
                order[1] = "GOOSE"

    return action


_V65_MAX_TOMATOES = 8
_V65_HANDS = 2
_V65_DECISION_STEP = 360
_V65_TERMINAL_STEP = 708
# Preserve a meaningful tomato shortage after our own projected supply.
_V88_MIN_POST_SUPPLY_DEFICIT = 300
_V65_STATE = {
    0: {"last_step": -1, "decided": False, "targets": []},
    1: {"last_step": -1, "decided": False, "targets": []},
}


def _v65_distance(left, right):
    return abs(int(left[0]) - int(right[0])) + abs(int(left[1]) - int(right[1]))


def _v65_tick_count(start, stop, interval):
    if stop <= start:
        return 0
    return (stop - 1) // interval - (start - 1) // interval


def _v65_town_drain(step, shops, item):
    shop_ticks = _v65_tick_count(step, _V65_TERMINAL_STEP, 4)
    center_ticks = _v65_tick_count(step, _V65_TERMINAL_STEP, 24)
    demand = center_ticks
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += shop_ticks * (2 if len(products) == 1 else 1)
    return demand


def _v65_visible_crop_supply(farm, crop, day):
    schedule = {
        "TOMATO": (8, 9, 10, 11),
        "STRAWBERRY": (10, 12, 14, 16),
    }.get(crop, ())
    supply = 0
    for row in list(_get(farm, "tiles", []) or []):
        for tile in list(row or []):
            if not (
                isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == crop
            ):
                continue
            supply += max(0, int(tile.get("yield_units", 0) or 0))
            age = day - int(tile.get("planted_day", day) or day)
            supply += 2 * sum(production_age > age for production_age in schedule)
    return supply


def _v65_integrated_value(item, inventory, quantity):
    return sum(_market_price(item, inventory + offset) for offset in range(max(0, quantity)))


def _v65_live_strawberries(farm):
    result = []
    for y, row in enumerate(list(_get(farm, "tiles", []) or [])):
        for x, tile in enumerate(list(row or [])):
            if (
                isinstance(tile, dict)
                and tile.get("kind") == "PLANT"
                and tile.get("crop") == "STRAWBERRY"
            ):
                result.append((x, y))
    return result


def _v65_compact_targets(farm, limit):
    candidates = set(_v65_live_strawberries(farm))
    if not candidates or limit <= 0:
        return []
    access = _shed_access(len(_get(farm, "tiles", []) or []) or 10)
    first = min(
        candidates,
        key=lambda point: (min(_v65_distance(point, shed) for shed in access), point[1], point[0]),
    )
    chosen = [first]
    candidates.remove(first)
    while candidates and len(chosen) < limit:
        touching = [
            point for point in candidates
            if min(_v65_distance(point, selected) for selected in chosen) <= 2
        ]
        pool = touching or list(candidates)
        point = min(
            pool,
            key=lambda value: (
                min(_v65_distance(value, selected) for selected in chosen),
                min(_v65_distance(value, shed) for shed in access),
                value[1],
                value[0],
            ),
        )
        chosen.append(point)
        candidates.remove(point)
    return chosen


def _v65_decision(obs, step):
    seat = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    me = farms[seat] if seat < len(farms) else {}
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    day = int(_get(obs, "day", step // 24) or 0)
    shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])[:5]
    market = _get(obs, "market", {}) or {}
    inventories = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}

    tomato_current = int(_get(inventories, "TOMATO", 10000) or 0)
    strawberry_current = int(_get(inventories, "STRAWBERRY", 10000) or 0)
    tomato_drain = _v65_town_drain(step, shops, "TOMATO")
    strawberry_drain = _v65_town_drain(step, shops, "STRAWBERRY")
    opponent_tomato = _v65_visible_crop_supply(opponent, "TOMATO", day)
    opponent_strawberry = _v65_visible_crop_supply(opponent, "STRAWBERRY", day)
    tomato_projected = tomato_current - tomato_drain + opponent_tomato
    strawberry_projected = strawberry_current - strawberry_drain + opponent_strawberry

    candidates = _v65_live_strawberries(me)
    max_quantity = min(_V65_MAX_TOMATOES, len(candidates))
    fertilizer_quote = max(1, int(_get(prices, "FERTILIZER", 100) or 100))
    best = (0.0, 0, 0, 0)
    for quantity in range(1, max_quantity + 1):
        units = 8 * quantity
        tomato_value = _v65_integrated_value("TOMATO", tomato_projected, units)
        strawberry_value = _v65_integrated_value("STRAWBERRY", strawberry_projected, units)
        # Four appended-hand windows: conversion, first-yield separation,
        # three-yield separation, and final-yield preparation.  This reserve is
        # deliberately larger than the observed two-hand hire bill.
        operating_reserve = 3200
        direct_cost = quantity * (50 + fertilizer_quote)
        npv = tomato_value - strawberry_value - direct_cost - operating_reserve
        candidate = (float(npv), quantity, tomato_value, strawberry_value)
        if candidate[0] > best[0]:
            best = candidate
    quantity = best[1] if best[0] > 0 else 0
    # The patched curve rewards genuine scarcity, but supplying through the
    # hinge destroys marginal value.  Reject cohorts that would leave less
    # than a generic 300-unit shortage after their own projected 8x output.
    post_supply_deficit = 10000 - tomato_projected - 8 * quantity
    if quantity > 0 and post_supply_deficit < _V88_MIN_POST_SUPPLY_DEFICIT:
        quantity = 0
    targets = _v65_compact_targets(me, quantity)
    return {
        "shops": shops,
        "tomato_current": tomato_current,
        "tomato_drain": tomato_drain,
        "opponent_tomato_supply": opponent_tomato,
        "tomato_projected_inventory": tomato_projected,
        "tomato_projected_deficit": 10000 - tomato_projected,
        "post_supply_deficit": post_supply_deficit,
        "strawberry_current": strawberry_current,
        "strawberry_drain": strawberry_drain,
        "opponent_strawberry_supply": opponent_strawberry,
        "strawberry_projected_inventory": strawberry_projected,
        "quantity": quantity,
        "npv": best[0],
        "tomato_value": best[2],
        "strawberry_value": best[3],
        "targets": targets,
    }


def _v65_route_cost(start, route, service_cost):
    if not route:
        return 0
    travel = _v65_distance(start, route[0])
    travel += sum(_v65_distance(left, right) for left, right in zip(route, route[1:]))
    return travel + service_cost * len(route)


def _v65_plan_routes(starts, targets, service_cost):
    routes = [[] for _ in starts]
    for target in sorted(
        targets,
        key=lambda point: min(_v65_distance(start, point) for start in starts),
        reverse=True,
    ):
        best = None
        for actor, start in enumerate(starts):
            for index in range(len(routes[actor]) + 1):
                proposal = routes[actor][:index] + [target] + routes[actor][index:]
                costs = [
                    _v65_route_cost(
                        starts[other],
                        proposal if other == actor else routes[other],
                        service_cost,
                    )
                    for other in range(len(starts))
                ]
                score = (max(costs), sum(costs), actor, index)
                if best is None or score < best[0]:
                    best = (score, actor, proposal)
        if best is not None:
            routes[best[1]] = best[2]
    return routes


def _v65_phase(day, planted_day):
    age = day - planted_day
    if age == 0:
        return "convert"
    if age == 7:
        return "prime"
    if age in (8, 10):
        return "cycle"
    return None



def _v68_fertilizer_horizon(tile):
    if not (
        isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
        and tile.get("crop") == "TOMATO"
    ):
        return -1
    return int(tile.get("planted_day", -1) or -1) + 11


def _v68_needs_fertilizer(tile, day):
    """True only when fertilizing now extends coverage toward final yield."""
    horizon = _v68_fertilizer_horizon(tile)
    covered = int(tile.get("fertilized_until_day", -1) or -1) if isinstance(tile, dict) else -1
    return horizon >= 0 and covered < horizon and day + 2 > covered


def _v68_fertilizer_count(farm, targets, day):
    return sum(_v68_needs_fertilizer(_tile_at(farm, tuple(target)), day) for target in targets)


def _v65_start_window(obs, action, state, day, phase, targets):
    farm = _farm(obs, _seat(obs))
    market = [list(order) for order in (action.get("market") or [])]
    private = _get(obs, "private", {}) or {}
    fertilizer_needed = _v68_fertilizer_count(farm, targets, day)
    if fertilizer_needed > 0 and len(market) < 10:
        shed = dict(_get(private, "shed", {}) or {})
        free = max(0, 100 - sum(max(0, int(value or 0)) for value in shed.values()))
        fertilizer = min(fertilizer_needed, free)
        if fertilizer > 0:
            market.append(["BUY_PRODUCT", "FERTILIZER", fertilizer])
    action["market"] = market[:10]
    state["window"] = {
        "day": day,
        "phase": phase,
        "base_hands": len(_get(farm, "hands", []) or []),
        "requested": _V65_HANDS,
        "maintainers": [],
        "pending_hires": [],
        "routes": None,
    }
    state["window_key"] = (day, phase)
    return action


def _v66_append_pending_hires(obs, action, window, step):
    """Reconcile submitted hires, then use the first later market capacity."""
    farm = _farm(obs, _seat(obs))
    hands = list(_get(farm, "hands", []) or [])
    maintainers = [
        int(index) for index in list(window.get("maintainers", []) or [])
        if 0 <= int(index) < len(hands)
    ]
    pending = []
    for entry in list(window.get("pending_hires", []) or []):
        index = int(entry.get("index", -1))
        submitted = int(entry.get("step", -1))
        if submitted < step:
            if 0 <= index < len(hands) and index not in maintainers:
                maintainers.append(index)
        else:
            pending.append({"index": index, "step": submitted})
    maintainers.sort()
    window["maintainers"] = maintainers
    window["pending_hires"] = pending

    missing = max(0, int(window.get("requested", 0)) - len(maintainers) - len(pending))
    if missing <= 0:
        return action
    market = [list(order) for order in (action.get("market") or [])]
    room = max(0, 10 - len(market))
    count = min(missing, room)
    if count <= 0:
        return action
    # Existing same-step hires materialize first.  Recording their offset lets
    # the controller retain only its own appended actors without disturbing
    # inherited actor indices or routes.
    existing_hires = sum(bool(order) and order[0] == "HIRE" for order in market)
    first_index = len(hands) + existing_hires
    for offset in range(count):
        market.append(["HIRE"])
        pending.append({"index": first_index + offset, "step": step})
    window["pending_hires"] = pending
    action["market"] = market[:10]
    return action

def _v65_late_tomatoes(obs, action, step):
    seat = _seat(obs)
    state = _V65_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "decided": False, "targets": []}
        _V65_STATE[seat] = state
    state["last_step"] = step
    action = _align_hands(_copy_action(action), obs)
    farm = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    day = int(_get(obs, "day", step // 24) or 0)
    hour = int(_get(obs, "hour", step % 24) or 0)

    if step == _V65_DECISION_STEP and not state.get("decided"):
        decision = _v65_decision(obs, step)
        state["decided"] = True
        state["decision"] = decision
        state["targets"] = [tuple(point) for point in decision["targets"]]
        state["planted_day"] = day
        quantity = int(decision.get("quantity", 0) or 0)
        if quantity > 0:
            market = [list(order) for order in (action.get("market") or [])]
            if len(market) < 10:
                market.append(["BUY_SEED", "TOMATO", quantity])
                action["market"] = market[:10]

    targets = [tuple(point) for point in state.get("targets", [])]
    if not targets:
        return action
    planted_day = int(state.get("planted_day", day) or day)
    phase = _v65_phase(day, planted_day)

    # The inherited tapes finish their opening hires by hour three on the
    # relevant days.  Appending here preserves every base actor index.
    if phase and hour == 3 and state.get("window_key") != (day, phase):
        action = _v65_start_window(obs, action, state, day, phase, targets)

    window = state.get("window")
    if not window or int(window.get("day", -1)) != day or window.get("phase") != phase:
        window = None
        state["window"] = None
    if window is not None:
        action = _align_hands(action, obs)
        hands = list(_get(farm, "hands", []) or [])
        base_hands = int(window.get("base_hands", len(hands)))
        action = _v66_append_pending_hires(obs, action, window, step)
        maintainers = [
            int(index) for index in list(window.get("maintainers", []) or [])
            if 0 <= int(index) < len(hands)
        ]
        if (
            len(maintainers) >= int(window.get("requested", 0))
            and window.get("routes") is None
        ):
            starts = [tuple(hands[index]) for index in maintainers]
            service_cost = 3
            planned = _v65_plan_routes(starts, targets, service_cost)
            window["routes"] = {
                hand: [tuple(point) for point in route]
                for hand, route in zip(maintainers, planned)
            }
        routes = window.get("routes") or {}
        tiles = list(_get(farm, "tiles", []) or [])
        inventories = [dict(value or {}) for value in list(_get(private, "inventories", []) or [])]
        orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        access = _shed_access(len(tiles) or 10)
        for hand in maintainers:
            actor = hand + 1
            if actor >= len(orders) or hand >= len(hands):
                continue
            route = routes.get(hand, [])
            position = tuple(hands[hand])
            inventory = inventories[actor] if actor < len(inventories) else {}
            fertilizer_needed = sum(
                _v68_needs_fertilizer(_tile_at(farm, tuple(target)), day)
                for target in route
            )
            if (
                fertilizer_needed > 0
                and position in access
                and int(inventory.get("FERTILIZER", 0) or 0) <= 0
            ):
                orders[actor] = ["PICKUP", "FERTILIZER", fertilizer_needed]
                continue
            while route:
                target = tuple(route[0])
                tile = _tile_at(farm, target)
                if position != target:
                    orders[actor] = _v20_move_toward(position, target, tiles)
                    break
                if phase == "convert":
                    if isinstance(tile, dict) and tile.get("crop") == "STRAWBERRY":
                        orders[actor] = ["DIG"]
                        break
                    if tile is None:
                        orders[actor] = ["PLANT", "TOMATO"]
                        break
                    if isinstance(tile, dict) and tile.get("crop") == "TOMATO":
                        if not bool(tile.get("watered_today", False)):
                            orders[actor] = ["WATER"]
                            break
                        route.pop(0)
                        continue
                    route.pop(0)
                    continue
                if not (
                    isinstance(tile, dict)
                    and tile.get("kind") == "PLANT"
                    and tile.get("crop") == "TOMATO"
                ):
                    route.pop(0)
                    continue
                if (
                    _v68_needs_fertilizer(tile, day)
                    and int(inventory.get("FERTILIZER", 0) or 0) > 0
                ):
                    orders[actor] = ["FERTILIZE"]
                    break
                if phase == "cycle" and int(tile.get("yield_units", 0) or 0) > 0:
                    orders[actor] = ["HARVEST"]
                    break
                if not bool(tile.get("watered_today", False)):
                    orders[actor] = ["WATER"]
                    break
                route.pop(0)
            else:
                orders[actor] = ["PASS"]
        action["farmer"] = orders[0]
        action["hands"] = orders[1:]

    if day - planted_day == 11:
        positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
        orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        target_set = set(targets)
        for actor, (position, order) in enumerate(zip(positions, orders)):
            tile = _tile_at(farm, position)
            if (
                tuple(position) in target_set
                and isinstance(order, list)
                and order
                and order[0] == "WATER"
                and isinstance(tile, dict)
                and tile.get("crop") == "TOMATO"
                and int(tile.get("yield_units", 0) or 0) > 0
            ):
                orders[actor] = ["HARVEST"]
        action["farmer"] = orders[0]
        action["hands"] = orders[1:]
    return action


def _v66_output_at(tile, operation):
    if operation == "COLLECT_FERTILIZER":
        if isinstance(tile, dict) and tile.get("fertilizer_available", False):
            return "FERTILIZER", 1
        return None, 0
    if operation != "HARVEST" or not isinstance(tile, dict):
        return None, 0
    quantity = max(0, int(tile.get("yield_units", 0) or 0))
    if tile.get("kind") == "PLANT":
        return tile.get("crop"), quantity
    animal = tile.get("animal")
    return {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}.get(animal), quantity


def _v66_capacity_reserve(obs, action, step):
    """Keep projected late-day holdings within the 100-unit drop capacity."""
    hour = int(_get(obs, "hour", step % 24) or 0)
    if hour < 18:
        return action
    action = _copy_action(action)
    private = _get(obs, "private", {}) or {}
    shed = {
        key: max(0, int(value or 0))
        for key, value in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = [dict(value or {}) for value in list(_get(private, "inventories", []) or [])]
    carried = sum(
        max(0, int(value or 0))
        for inventory in inventories
        for value in inventory.values()
    )
    farm = _farm(obs, _seat(obs))
    positions = [_get(farm, "farmer", [4, 4]), *list(_get(farm, "hands", []) or [])]
    orders = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    outputs = []
    consumed = 0
    for actor, order in enumerate(orders):
        if actor >= len(positions) or not isinstance(order, list) or not order:
            continue
        operation = order[0]
        tile = _tile_at(farm, positions[actor])
        item, quantity = _v66_output_at(tile, operation)
        if item and quantity > 0:
            outputs.append((actor, item, quantity))
        elif operation in ("FEED", "FERTILIZE"):
            consumed += 1
        elif operation == "PLACE" and len(order) >= 2 and order[1] in ("GOOSE", "COW", "SHEEP"):
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
    actual_sells = sum(
        min(shed.get(item, 0), quantity)
        for item, quantity in planned_sells.items()
    )
    needed = max(
        0,
        sum(shed.values()) + carried + sum(value for _, _, value in outputs)
        - consumed + planned_buys - actual_sells - 100,
    )
    if needed <= 0:
        return action

    prices = dict(_get(_get(obs, "market", {}) or {}, "prices", {}) or {})
    sale_priority = sorted(
        _SELLABLE,
        key=lambda item: (item == "TOMATO", int(prices.get(item, 0) or 0), item),
    )
    for item in sale_priority:
        already = planned_sells.get(item, 0)
        available = max(0, shed.get(item, 0) - already)
        quantity = min(needed, available)
        if quantity <= 0:
            continue
        existing = next(
            (
                order for order in market
                if len(order) >= 3 and order[0] == "SELL" and order[1] == item
            ),
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

    # A product/animal buy that itself crosses capacity is cheaper to defer
    # than already-realized farm output.  Seeds do not consume shed capacity.
    if needed > 0:
        buy_priority = sorted(
            (
                (index, order)
                for index, order in enumerate(market)
                if len(order) >= 3 and order[0] in ("BUY_PRODUCT", "BUY_ANIMAL")
            ),
            key=lambda value: (
                value[1][1] == "TOMATO",
                int(prices.get(value[1][1], 0) or 0),
                value[0],
            ),
        )
        for _index, order in buy_priority:
            quantity = min(needed, max(0, int(order[2] or 0)))
            if quantity <= 0:
                continue
            order[2] = int(order[2] or 0) - quantity
            needed -= quantity
            if needed <= 0:
                break
        market = [
            order for order in market
            if not (
                len(order) >= 3
                and order[0] in ("BUY_PRODUCT", "BUY_ANIMAL")
                and int(order[2] or 0) <= 0
            )
        ]

    # Once saleable shed stock and avoidable buys are exhausted, allowing a
    # low-value harvest to execute merely replaces it with an arbitrary engine
    # discard at midnight.  Defer that production instead, keeping tomatoes as
    # the last resort.
    if needed > 0:
        output_priority = sorted(
            outputs,
            key=lambda value: (
                value[1] == "TOMATO",
                int(prices.get(value[1], 0) or 0),
                value[0],
            ),
        )
        for actor, _item, quantity in output_priority:
            if actor >= len(orders):
                continue
            orders[actor] = ["PASS"]
            needed -= quantity
            if needed <= 0:
                break
    action["farmer"] = orders[0] if orders else ["PASS"]
    action["hands"] = orders[1:]
    action["market"] = market[:10]
    return action


def _v88_late_plan_active(obs):
    state = _V65_STATE[_seat(obs)]
    decision = state.get("decision") or {}
    return int(decision.get("quantity", 0) or 0) > 0


def _v88_late_tomato_overlay(obs, base_action, step):
    """Return byte-equivalent V84 action unless the public decision is active."""
    proposed = _v65_late_tomatoes(obs, base_action, step)
    return proposed if _v88_late_plan_active(obs) else base_action


def _v88_capacity_overlay(obs, base_action, step):
    if not _v88_late_plan_active(obs):
        return base_action
    return _v66_capacity_reserve(obs, base_action, step)


# V107 changes only the timing of the day-0 WHEAT5 product order.
# It is an empirical policy candidate, not an exact V92 rejoin.
def _v107_index0_opening(action, step):
    if step not in (0, 1):
        return action
    action = _copy_action(action)
    market = [list(order) for order in (action.get("market") or [])]
    if step == 0:
        hires = [["HIRE"] for order in market if list(order)[:1] == ["HIRE"]]
        sheep = next(
            (list(order) for order in market if list(order)[:2] == ["BUY_ANIMAL", "SHEEP"]),
            ["BUY_ANIMAL", "SHEEP", 2],
        )
        sheep[2] = 2
        market = [
            ["BUY_PRODUCT", "WHEAT", 5],
            *hires[:5],
            ["BUY_ANIMAL", "COW", 1],
            sheep,
            ["PASS"],
            ["PASS"],
        ]
    else:
        market.extend([
            ["BUY_ANIMAL", "COW", 1],
            ["BUY_SEED", "WHEAT", 7],
            ["BUY_SEED", "MELON", 12],
        ])
    action["market"] = market[:10]
    return action


def agent(obs):
    try:
        actions = _kawa_actions(obs)
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
        _observe_opponent_market(obs, step)
        if step >= 708:
            return _v20_terminal_action(obs)
        action = _weed_repair_action(obs, _copy_action(actions[step]), step)
        action = _v17_feed_guard(obs, action, step)
        action = _v17_room_evac(obs, action, step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        action = _v17_r5_counter(obs, action, step)
        action = _v17_md_counter(obs, action, step)
        action = _v38_farm_pair_tomatoes(obs, action, step)
        action = _v73_route_tomatoes(obs, action, step)
        action = _v71_route_carrots(obs, action, step)
        action = _v79_rival_strawberry_flush(obs, action, step)
        action = _v88_late_tomato_overlay(obs, action, step)
        action = _v35_egg_late_pair(obs, action, step)
        action = _v17_room_guard(obs, action, step)
        action = _v88_capacity_overlay(obs, action, step)
        action = _terminal_liquidation(obs, action, step)
        action = _v107_index0_opening(action, step)
        action = _align_hands(action, obs)
        _record_own_sells(obs, action, step)
        return action
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }

def _kaggle_submission_entrypoint(obs):
    return agent(obs)
