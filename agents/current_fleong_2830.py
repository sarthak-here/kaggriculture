"""v21 tactical-memory Kaggriculture agent.

The field/labor route is a fit-only current-submission medoid.  Market-memory
hazards are balanced across one fit-only medoid per current Top-30 submission.
Runtime uses no team name, episode id, seed, notebook ownership or lookahead.
"""
import base64
import copy
import json
import math
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    (
    'c-'
    'rk<U2j`ia{MoP*29RjJa*o+HaBCeXKdJ>B{qgI7$6%22sRIsyaoC1@mL}+dAqu*y3e8Q4fe@2CEa_zPj_{7^~e9Y`nO+y``cfCyZ'
    'Wb(SAY2V)$5nPyuEw>;pca|tNZJ#fB*GA|MkB<{p8cfzy12#fBf~oKYjlF*Z%U$-'
    'A}K6ynB6hef8qa{_1*rf4%zp{SUj{+pFuF!w=r?b}v7D{p0TSo1d<(zh8a5|6zCc;nQz_cliG8yEiX?e(~YtN1y-'
    'XhgYB5b@*`qzt^YD|LM)U4?mnX`{UJq_x{7@KY0Avc}Lu*9KQN^_4d_^KmGjn(Cw?6&tE>gr1$9ckbio`>$?}b$2Xj`9KL7u{7--'
    'S(=ujB7mh=6{17`u-m$;?uzRQa5Wkr-'
    '5yz+O?hb8VbvcgTv3HLvN%ZgVz=xH3_IB_t@a*elj6PnyfAjNt<vi|;`Y<m~T_#hkOfcB%_dJX!Tq%G2eRJYLX46?8(8G^DUcI<G'
    'te0bF!+bve|6v^O<Ixn)j{C~sE>nhv`C&{-0~+_)`D%%yaQush;plXcjQY~m;{<~<;qLwW@&Y|?cD6g$--I{W(-'
    '?<(SvASdJa%;XP1RE}l*?LK1}@(#oiUA%TPE#vi^xGOjNLMQpPwQ|Yr={=z9)V-IY2w3mp`~MW{-dCJ-'
    '@QRD$iYg_zI6*@2n@>Qe2sM+KhW#;HDL)jfUhXc=6`-'
    '>)neFzx;9c?!&9sum0ut*&+{)tvYU#R;!l7a<m=C10miPtG`9BI_nYod9#1V(UGkJ`<B_f9kac#fK0<n+Tz3xSe~b!!di1Qf*-'
    '&7x~*A1u-TgP52KgmN%K0bik*ABk815YF%t^yIs6rTP~lz#&pED~Z|gCOSErux_?u%7soZ4mcdvhkHBL^(>nF3XGK7@eq=?9q`-'
    '@$Du1QC_H+&ZzZ?$xwbo<b?gs-@Qqt%~l=TuX}0-o7-'
    '5+Cnq>X8R0xM=3A54`Rri~y{$BYo)JyI^x#R}8p7zvAd1zj(wWEjUxOHDmV_g!TTuZr>^Q=Kssf_aB$3d(ru~D!n`U<Fa<VXN(ZS'
    'dgodmCpX3lX*0ZA&-1#Bd)j<l>KJxC&G?w$SB<vth=TQSf-lg*A^({8q4Pb`>6h&6YjW_aoBX)d&G{`n?d7{SZ|$eSTRH{-'
    '#%}%XS0n*s(K{Assu>t4@>&aCgFU~X!#22Ewg}KR4za-G{RrS4HkdL~?e2_?FvVPmC-YphfkkWeE%n3QyFZ6(W%)9n6?Q8O#Am~*'
    'IBm=Ea|(*R|M2c^|A*bXcYlf0qE@iqxmVF!Huv)MJnb0@JD+3K#+h{Zi<3c+2Igra0<pmy=CSdNn7oaA>dkRB#<@vjMWMoCjV*_Z'
    ')pHp}7U}Z%b;PHzUbC~C@l{gx#sUv6EgE8u(79t_od&E#_XK$OFzS?#<Jnd=O-'
    'gI8n9$yktxfw3%;bhmy6y%v5D)Q?&*V`PD)M)OA`+!L{+uCulQU#jO-M<&!Yr&?iya_G(HKWUGZEHl1%dI{tgNT5Wu6Ssg-'
    'D6PTxtL@k&7FSy6z?)j12)M8;E`Qh*-Rfs6#Nvq?Ht4z)5WKtaCm~$+rdG8kmU=3P>n^$-'
    'Y6i!;0@a3ttBVdfZkB7$dYQ_mvbci(K|&a~{5#)X5`?lZVr;55HvqFph%>*qf8UJn-'
    'b@Qk?SOI2$7nT6}DSae1M~hLh`Q35&ZqF}EI{u$|9{X`^$SuMawHCI{~>gfP)D8an^tU;&6z(;eU$qi{`oiZ>NBvok0K)bzNWQ8-'
    'dwzmF%qh-wzb>#)1uy!rIc)5N`s7=PfM16#tU2gk=PePOokAYBQ7E}d*DfY@-'
    'zwHY8>hr%b&tfmJs0VXgj&N_+p)Z#6faaQ|*W|VanCko6@BeevzaDWU{GevF>;L0ce<K<OAS{4ANYMUfidX>8iVD%?BdQriuSfrC'
    '>gI<o9gUG2ZW)SRen;JX6>ybDcjkE+9IDyhKuI&`aZck!QJiTU^mIWpv<ZG{xZ{2e>`w{#(P6>*d^rM<&?j7g?#sip%G2gNW`y&Q'
    'hRukk8*b|MJf!9KVcMe|+Ms`#HrejCsEmz^JscB&LiXWl`CL_28Xu6%^RJFoem^Wt_EnZJpB09)qPEwB@ODP_^09m6$CSMT`IPjD'
    'j4Q>E1jq|~@Kc)}`<C{9eNZ5HR)YXLVpy?}#C?1pE(e4T4o6Ju2O;~6nd93W~DkHB#df66&vQpkd*@4TlkU^@l9{?`FqqP#j6P6~'
    '>VyeYgVA{;-x6KIirb?I6WS-?{i~Tt6T)3<rx7m-'
    'cUjONL;H(0>L_2o<s@$+daidjJlD)pk$aDqT&~f^Y4OV;w5NkP)qg%_t>tU5nhTeOvy{*hF!cRN>vr+y4r7gr&C5fM!^I*l)yOhE'
    'Z9X(^Mo<~aIQX0xx$?<o`d03Bo%?LhQg<(HX*CLKW2eZyxz-Tt30Rv4w_sHk35eScp*>XZU<9bt+SRwSlV1vi0I>~OvtVq=U`o02'
    '447+Wu{Jt)&Ht9aox?^g7DeFg#5^z9PF|o53LN+-'
    'dJauxoqF>@D|5;1JnkAYAc5IWpup<6gfpcioWoZOp3<W!l<zt&6)Lh6DG%8+#(XSlH5%;pP2;~(V@3&3=F*8R2Mdq+WPg{B(zv0g'
    '0hJ7uf2y0r5-&*VKZlh{XAWMR{zra3PyOF0~t*(M5VHCW<H&;(XVwpt}%<b)fwhWV;!RFgy$MwjM+Y0${pWiF-'
    ';<hu^EmQ)Su++7661B#d)@%_6FIB{Oq(MntwwJH|+44By7Ra5TG-}iF^gEFx-'
    'yXNtzOn#wM$YlMa!pd7tD|oScwVd4(B!XV!<N8kc9xQ$)oRv=p*ZUL%HZWG-iXIeKB6&h0BDG-gTN96%@Q*}#^QfG++L#>#<8G?0'
    'NqEkg1pix05LJJ`GBr`EtM*c&2hrd7bh^t-Pk+mL^~sq=q#g#rA|k~wIS3o)+`G4tQ^-'
    '?xFEEP1n2k|MSoh7YoDaKizA}WAV>>VI%}jkc44z@dLhV4n*S8P(a$89<}-'
    'Hf!P?7W=;h20zUg>@#X#ffWlpj$2jUyihEZ7o7ZgDe=8R$5#HdC?w{2_CuS#PRZJEe*oSLu}VNl?PdSGCuMKIe0m<npR;%p9(`v5'
    'vgvq9|<Lo-*__(5l*dU2fPSvk5if5(!SU?{IX#VMQ(u=|vjE8=)I6pB?+&h1j@k>)U-9)*~Ul*dP}8<|Q%lzpKEJaF-'
    '!IwnTPN~EzeWG5;?tTd-'
    '7?uCbRhe{v=S~1E;r2Bl}P$Q^vPGFUvJe^HBuV7^o0A`P_dB7^FSywc5o1SUNNuo@plU;Jgr`e`ifBAmel&C2<@XQR$Jlx;4ty5j'
    '4WM$270h+pH`i0GrV?l%|wRQ73351I0F4S0Boh-'
    ')_@YuoQheQJIe3jm8>{Qf>V;Uov8?wlsjz%!YT~d+c)r=|n52JJR%sxt<m5vM9KPW-RD?)CHCKjo|1Z<@kQc4;y)$MDg0|{=7`nm'
    'eW6pJuAcx!Z!(TgB`P}yQ6OWmD^hcKR%EfyR`mPl6!VkjoGA7NzBc^WXSsd-'
    'i+lV18dASU~Xs*vF*9n~nD;90~V#KNRC6$x!6Vbmpvdc$mcYcj&0@gX`s1{+Zjy#_v9639u}xBZAGlF1N*N&|1~i0F?WLkiOHxDk'
    '^yl5>^lrIjVA&U_jMkMND&KOB(pz3;f2r4K*0HhJc_+W0(!lWGuJvkgdec_C#*Isu5E6%p-5?+cM$CN-Yxtyblf!0F2efHh`}22G'
    '~1kie~G9Qv?L0y9m9b5qULIH$qfa&s+qF%4`ZKruS=TxP;aX7xx6pn<Xw2E_fN2%^LjyyC}?XV@*l6Si~X+~ep1n&X)?Ww{!jM}f'
    'g<@;Kp$DMbC18&6=uUR`Hk(8mvi!UQ7!wg_Ccp2SHOkIpj^`Y6ln2r};JZ_h7(9h(!W)4t3bpj|hVIjDk)#bIt#lp=ypB3)D9Ml!'
    '6=%(xlFRMQG-S*em}i~G7c4J|1eELQ$>i)-'
    'n_hb&=^bJI!YR&k=O^oBHBP6ay$OQexo2b}C++FT8_roGLb4qYH9Ps*+gTs&OPyyQsZ<w0##3}>R?7?X=}7|-p}JR2=d1|(-'
    '5(@I2nA|9D6Zci)cv;bz1ElpEChigfZ8hIxaWSorP$#hZ3QwQrM2`9QiW~vEwQq_96B-'
    '<I}jk}BpI8`N<h~rgq+CWY*8_6FojT=?yWj0bnC$^t?z~nCK0<$&8eS67N=7~gr%n_ZOUhI<r7EK<oY@bF4-'
    'yok9r~oYgnB|8zJfSSXd6<(9lUf|Fy!JNP$Ph9gGdiPru6#f0&k*j0FB!0R`S~{Wn-ZfnCKRu4HVq(%$tZ%X9ZJEBY4S7l!6=(51'
    '4^Y+KAB*zc!V^2hR`UM&*FzB!HummiM6FuP&bH1SJnU;NEm^knDVrr6pJuCpCzH(MZSLaUKLYhgB2mM;3D!8nCmhvcINS*;tmSj%'
    'UoaOHxj3|3F$Dx12b3?;k3$3#>;`dkirjTH+r-T4Ce;OsJ-'
    'LfmAn!*a?}Ii9-V&~u)(6C`4T<8>Ey;>DtZM7`_h)oOCV?MV>lC7?F*cfPu-VkX55n?W4nIFR%@2b3Palp(3@|_<E5qD^pdEk=lb'
    'DgmhFj>(Hg26(T9bxFYsCnw$D<rVj=xwV`45zhIY$XHPv<#+}>@wd<|3~&cwrAmR+9#YGwTcJA;v}Yl|a}xLaB>GQXw#r{Yvo!O}'
    '7_ytqcNPI-gT8dI=%aY+l$E9B8q+usjp)4aW%L-'
    '_595tBe0qmlz)rkGmmr{?+m07XGh<QO_aF>#Bc_9DUs_fk#Sfgybl2(p3<U6vz54-YFhBh70!3Rj84MU-HQXDPgeZ22}~|7WM;9T'
    '6XehKEDuNF4M5RdAj!<!Q{b+=B{7pqV7$iHqPt&q17;3O%c4<ikU5m{XJR;=n~`jUluFBVIzplD59~6noXeM<f&^7Bi=b%t;O$7L'
    'PBlr?x$0q`22Y^3vjKy`~B5$%^ww@$zonsZxaf@qtD`)SG`q*Hf?|l4*pp!*{I`u8rV&r@X7>-1|CQ-DG!dbd%t}ogmLtWc||UrM'
    'SOv5+T9^07|ef8rl5YLXl8AbF*Lp*!d3=iXjs*V32kQ{2(3CP^LX0rEq6Dhdo+if9_(n*(fw4jWZlPkCm)T)i&4X(DhR~Bb!RdDb'
    'J%7G-BABxx#q$+E!wcm;nM_T9tK11PR^3#~vM^Mf)eoC2TQtiVjg-'
    '3r>+YKj||vwt*5ETxHv#QQ)>YqkTl$04pcmOsIF$0Zf?XgcnreH3Z@g@~zlPJ-2P59J`5iAM9;E(u)Qwxi*dt7!9(U-'
    'r1V3oK3kUdx+v3p@4B3%AOiI_ZEQ1b-x&Ae7fiA2fUQaNo!$!0XMeJ9p9#@A_d2uXZPiCZ8mPFXG%c~#!B-'
    'BVSEL1QoR@v3K{S!!Kn)eCS{EeR8NxW+`zT&apKYOk*e|3ShZQep{q^i=8BFkQGos+)og0!j+1H?eY+4DcMWpaMceA=6{{e`e#UK'
    'QD52`djhU{GQG01ucil)(m<<dInqi)Vk&CZ5I$k=j_Z1qsj(f?%qGoyBWD@i0#p4;~__o7|1HS%oe-vqj1wm=WvF8ZrR>F;*%goC'
    'U<;8m|AeqRCj{X`NEie1I?Bko(;#T_@NjU`IjUA$oljPVe>bJqrSF6G1TMxUAu?(@BknK?i+Bwj{dyJH7;6<7VOj?GQOf;x97B(+'
    'nu+s)bH8U7^-'
    'SqbibGd1d9GwfhOXqT*`sL?$!g*l(Lf$%HxQu$%z%3mmxUU~+LStb;RmZ~TzpH|0{H~tl2vLfc2e*`z(yaNZYPC5ca=-'
    '^RovHydTe`Eb7k;9kTWn|&U7jn47kdee$*knq5Z#rCgi?~Q?n+*uXEb_ighk<)(s(E#ZJ*nWl@vrOY^vZWTT-'
    '2l?<fUgQ$b+S0h~u=Vl0FrxOrBsy1m*p3jNd2%*BPIcaQrUZmne~Ayd6p)`2mSs{<c(tCEn~-'
    'qELycNFy~nLJ&gC^tc?&KL3d|K#dW)#&jFIwQdg<Nb`qLiHAkN(KYG3S~wBhl%209!Uh$;ZPn+MCevUm!+^Fb^DVe!;f?#E-'
    'aR_i#|SD9|wel!|N-bu}Qtpb`ZcGsBfR_V$w((d-'
    '4DkHVMqDE^^TEVsW}zRca^o$ct)pbPDC_K_v#d14}BaU#w~Aj^VliAT&GBFbN|)yExrpR4U-'
    '_iTv<j7u^)=arQwM*&&t&#xem4hN~q+z}|)SqEmLgQmk$>O}PMiqDg|c?cP<D>AqBDL6+uQ%-'
    '9y7d!Mi$Gq+7uaF$<Bm7Qn9VpQr{Q&~OTZkIVvbnQu{Ln=ibJw61*)C^rQ08&IGX3&{HKnt7L6v%)nj06pOnt9ClDLbo<(l~buo|'
    'g>FkaY$#4aGSm3=q4O=|^0NpZTdE0eey&N#b8w2RT!^%01ulT9lL*CF9YCFhGf0MKZy(RwvDHYL)h&3IHhu$IQ|wk;S^wf~ImLZw'
    'uR>0B)h^zUL#;X48yw)>cLh86zCgWOB-hrJW(y=)jE;85CxIJf&55$#CtAY{O{s1oNx?LSmZ(QUnpstTv6{taBU2bR}Y13%H~lrG'
    'y}CU=fxE6%=kZ7l&XNf&CkhWb7(6ZVQ-6j0^kv2vjg>jG1D@-'
    'J|!!pfRQ?sUOhK)IDx5UkqKM1U29XRjoJOvu!UcsViaOsXJ%h_9U4D%TK3CB23Y+C4mv)u09NCW?k@Fw;r$t?86!!IP#ld@bx*w3'
    'VU_*DQy?G5U?i|>{$^FmI<yM-I{K@@KzmvZvuJ#`6vtH)VEWDa9QrjSXCM5S}4b##W6bhOw_-'
    'o@qRza6ZeTpo=s6^%?NLBto{7U9Q3UXvo|WPTx_eT1=V<9nP2q+rGrb-'
    'J2vo;s)bm|xuX?RJs*}bx>~vaY`|z@2$S^ZzuzdP2b#32)EID(gi?bd2y@v6K|lDZ?Qk2_38`o(!<<r_!SF_h$rxV%3b;Tzi}iO1'
    ')SV+Wk*%BCSf=o{nLVmN4KL9i#ShInA_NV{LEu3L3W0Qtk9d3Hn<o3L><i}^e)R0geI+_o1R?BdYszSBXX)_diKt=7qWXk|EvsA7'
    'QDxM1Hdsi%Vp0YWGiaEv0eS%anM$#e@fJ&(5|;sUByt8^lcox+qz2fQ@KnjhOahkgGD2w3dux}wD_*fq=SZDU3&=^z!I()dVj<(1'
    'Lnsr>L2+x`ngy_XvY1qC)+rU6oLZf#q8eM^QG7oIuA>lHkt@MOG9p{kkjbZVoSrsKE|lBEc|l~93916cz!inA<lyo6`mJ$lsKgJ('
    'uZX{-'
    '<RuFMRsS_0c>zpMH?<=!LokQz#UO#9<{h`f=`14!)s%>R8g6%4p#OeU>H=$8JpFRH86lE<;RKEGUl_^B2njH8n#+U=gj~wLHRLns'
    'X!BY_<@yawYTMJzF!72CiGmei-'
    '#biWW*}FSN{Xoh4;hvfB}AbqAZ%w_WTU{TXzOXPni;|h>*;@{^%^=+e!+k7iR@e+#LuB=P!~vLTav^@L#{Yw3l)|l$>%c?gOp}SX'
    '7eZ7f8rcil^M12=^MS=+z*KS(&Q&brpO12NhNUJRt+eG=K_=OZ!2B^Nr7IH0C*WboQ0H)t7t2oKduj<GRrFvW|k;GVG&(gki>FDo'
    '*XP4w4@0p#1(^iP+J<5d8Tm_V00;ZP9bd<E{~KbQUFwFee<daO^XoW%D$>`O`UNs=P6d54fPMjo#|Hv=6N*7Ry!io0(<0dV!VN90'
    'WeNMYccS~MKFu%L9nBpk7xpawOE*Ji~#rnSPrl(C>drZ{1kx@N0W5Z>pC0vI0oqw!jRB@XX(>6o1Tc;#O4!85Fmwv<bAqQpRLZi('
    'ADOfmle4jt%c)1ngkRPsaqhu7RW7mj`<kNg$Z^vlYo45iut9e4?-'
    '4z+9tyR`qB*SJ$VAAY$>gR#9d9kzEFstQxg1nFhxal8QXTC+AGmxWB~vhgVqjmQMgS7+-'
    '(+|wX^}`WQw%xcJJV30^xEzLqw<~8n0+pCdg+qp<u8`+`>UBX{e9%61HN&S;3x=q|@z8(GXh@;DRumSpx#-'
    'axhg9bgGOTdpTr;m0VaJp$}X*rEUAksqP(bWF0|4H4J~aVYvwc<-p1IN-RTr3F8x`&|h5~q=ZL-ykpKc;)PK8iqt81Pwy+aWT-'
    'G_CBCSTRf-+ZZdG_+Lf2*|<$?rSl;=>@AfbeN<271Vwvs7f#VWdyw1ZDho_%?3*YRdGf4II@ju91ENoG-TkfWrMS+hY(Q@rNoC@~'
    'ITcBm1MD~YR+yT1n;(W#3W(B_%L1Y}s!fyV#jgx$`llH?>M;)Tg}mDVtBlj=4XBBX7<hEh$VY|^(XUSsplx)r0@zG^7|x3bmf?jF'
    '<5wMk=c?pGXIpUKnff{_F@MCD<ak1T0a$;x9ZYlM2WsmxJ)V}xwrJc-'
    'Gp5`2AUS|QcNtg-9asZ=9blsxay2592^VJ=FZV%3SwM?Mr>AZkxgrb9N(CB-m-'
    'T>9eTs<snNrkhr<hS#5`DNk`+{c86WASOF#{i@Sims+i>qag`%d4-}233Vs<1rh=GnL&W)i&zyqU&ytYij(+-'
    'l+B(H<4lljti9${q;#YrC87#zJp`Gb*%>e%TN-'
    'Y02j9qGm?ZT}qlO(ppaQMaOTk5IyPmc=n1Ltd8Ndq|_R^Pi^CIz01aB{BswT2a!P7OKJcZUJqLQwdIT0k!1*zwaHKXl$FpkGRGq?'
    'rus56;=v@NW3)7~ZdF{Vym9UY`VdXSqZ<6KxYbycIy^NYhqs36xD;eUOh?8UR2IAdkr4zMp7LO?SPBV{55m1=uDQZQ_OS}Dle6t>'
    't__(JM_lzvOXj&L~}+m1fA8qQ`#>zW=&#Yd8E?5?V#JVVNc>2O;C`5sFWD|+rmG^aA7uB8zqk90xlAfmp<?t<tGkSPZhbBVwFSOs'
    '(gT%!rK<1E=lUnaT%zTT9og4foO*p{b1PT=W?^?|iHsh2E6QfyqAN9t4uYGMeS@5dQeSa&^kp9sDjtrOp$76NMVoDqqjC(hh?!c|'
    'G#Tf7$d5#YG7q}2?1#m(m47jdPp=L8-'
    'mYIhjSeKXyO$hIot&DqHi5@ysMbCC%5tY969sq)n0G%?eB=o@3)p{crtEGN_q5AXS^V4D9+64lwzsrk?cg*Ev!n~>JdHgu@#)JoE'
    '3uH4Mptg7}B<fJpC<1)@3+A)?dH(U$q`>)EdnJU@*CD4(W=Ey;}C-((0p_Y!5hnf(UO}AteOUGf^R{KF9WK&W85!x4y-'
    '{6#z8K~R?&0<0Sq1E%&-'
    'MnbX**5AK?}CXE3}r!rm2tS9+a<?cW5&i(sJ|QG16{f%rz7RpRmrvDwX}Gn%+huR3dyWvgk}C#B(|iKkT2ODA6udr6$a5&FtH>x2'
    'EZS#A;k4e;%w35kt;pbVh6y~voTPqI90uWCoO(xTPNWJ0BMr?g6)wfEIJ<Cb}=gElXeOr92P7y(#*o$H06c?R26kd_h{IAq#>#iu'
    'U%hH`6M0+G+EEf*g?3En~szvOeC;9)A6Dq_cGX)FQK}NAKe5B2$R|axIj3h&s9q*dzK4@FIfs(wx}YKyTVqC;l6fnOy5Eez-'
    'p{s&3fDG)#-G6-xs)!{7_X;E(&G|!FeLq)m?7oEU5Rt@2cgNzP&g&V<-'
    'AtOvdOUxlSNl`aD@`&pRc|XaEDt7VMnt_&Q_2IGBO^S3*GEzP|fuc_aR&DzDSBQB8JfY@NzX5Ej)S8OBHf%jA?oPh7LwPuHRHBqi'
    '_67Nn&X<swlKIzI!@vRsJ61qpr>TSb*rEi#ZNOcBnR*pzso3muUNJSTgnQ4aBF!<=7gMICKHS|(9>(3S2ko2J;~`d1L7h|ndC;p$'
    '^|B%3qaoS3HvmTJDm0NRx9{Po(p9s-&o+RA-dl?=cqxdLIP<lHL5n@jP@mQs&Cdg5te$Bt#gihepa3KXh{dmpmH@?T4{CG=v|N+r'
    '8eMREbWOserknwc^*?c<xK&sY|LZ0%C`rnY9tgp1T}qRZZ6h;gBJ#7=SVLa8jw7D^>Sr5)O3E_}q?+1)M-'
    'XLft7zNt&wu#UyosqhnD55<*HsX-'
    '87nN|xqZ0Q}oor(_%J6n8_NcfQ*jpiEH8bcXWY?&E1ikIQVX=H4H(2G8&oiS?GAYvAemdl8QU!ts?MAm#gqW&}GdHy_{=M`b0uG~'
    '`hXMRmPyB;1K(w<{wa_H?+J_Z+TT2P*%iXOq+%%AHtS)T08df#OlP^RbHVUIDQTNEiFLPeSQR=t##x2WSC0)sLYmGh4F@b=z!4yf'
    'KRTh!jlnB)Ie^o}ZtjeY{=tYp?xC!?TnO-w_8jTyLejbBA73<@w_tJ`P?F&VQgC$^BFCG<?XMadAdk{A1<CMbPWU$?uj87!)+%`n'
    '{)>0c$DEmk7HFzaj1RlAn*#?gHmqvO$9eT<WwyEY|vSn`WNYw|5Ys~40w{d*@s?K<s@`01oSWSMt+Q@cqh)XgpUArSzt)>}jeR3g'
    '40WixG^h+`12sZ^P+E29Ho2$Vb@0t#{1NNRA8dsMASmifqEwHVnlzkVhW4GU134v7w*GjSqWQl(Fg3-Bm{5y-'
    'j%?z8`tN?tv^yYR85dbuYRQ@C(OIULLigsE<TSa+q2U0Y-'
    '!vpv1?3_cZ~rf|(xg7L~=sP108oSB_Y<FV$fvOeS0MwHfRIrcJ(564yn5qOr~D6NOuH1W)d_X6HLx?M!DEa+aXQ|;?0y0R^p>g_&'
    'jZImSMsZl_QFeSJEBHUOxL=-'
    'h~R7skZzkTH`D#77MSJsS&1Xev0v8YHTDIcps9%T*+MRqGxq+Hl^G_5T2#G$*qvlN8J#>_3Q1{3uFlnXo9%+8WHCsNGzvN!#DLL~'
    'wjtKCVVWL<Y&Hq?=JOeARleSm%yXQ-gW8pkh6yhf-YenUzsI0cDBUK#`_Nged1p$R>Bt?Xm}LF|J#cywONmgcoQS_8KkwDD{Rb5J'
    'o=mY6793fJ{i_XMG_8ZWFAS*7L>G3y4{NKDeLB&0bs1=KsB&LnMYcY16MRwfu;@f!VE5``Vg8uzWzShTpEjL6A6v4US%5Z<LepI3'
    '3Rnard_##C8h+>1i1C}poSHA>8xf*9Qva#LJ65zuCBhjpb=PN7P(BlI>xG_4R`XdD`ea<V&UZ96=x6c+X5380XOIB`l==&{eVJwO'
    'YBstnS>`W&@5i)|c`nD5+*HId&RqjT~00uemGv!yqELCWq(*D=-'
    'Yh_YhrQ<PI=eJa(LvSWLs!Dp#=p{X%!X$zmyI!KRL@AE=KJvW4Zh?%2CE7P@J8D=uH&WF7dG7oFw)Ti3U^=>EFk$w$+I1USwz7G9'
    '5Ow0|LnEU?&d6kZ1'
    )
)).decode("utf-8"))
_HAZARD = json.loads(zlib.decompress(base64.b85decode(
    (
    'c-pmH*^V8z5&aiEUl?4AWZslOag4|jpa?J$!(S5Q-;-f+A~(C5=kVUnJP8_3aVyqxYUzJ{a3B8g>#rYv`OBw|-'
    '#$Ft4?a#mkNn$jj}IA*@^7OW8Wr9~c{pY4!vZy@Puwu!)>f&t1xHZ}ky=~G95p@OKY#lA?WfN_{qxh;x3SJ98Q}s`ALb2`UZ$ThR'
    'yL;JSZXTP8ZO3GV{ALFw&-#*cSRET*#%x_`R##s-8o3~&j0lB>(?(U-'
    'jIz`m&%VVo*LWFs90xIk0X<wdWo3t9{9MGmTvv$PoKa1%^p_YXrUV}1(A_HtWqzgG>Tv9+t}(U*;={B(#JN>Pv16JyG{3YHGO6{!'
    'M|P0cg}Y9fj42^as*f0FQpagt+$Fep>NX9D#d!j>^t{9BVvgmrrK%NV#ebh1395O23JHiFiTWD>t`e2q)mo)KgehQgL@=*p2e2!J'
    '_cTT`AAv_(Gs8a%#eL-'
    '+c@9kc)9FT+}K*0wq`#caHKkK9unZom(N#^mS)qO4zx}J!XRY`kxr=|D0ya8SJxmO^8v9%<v<D87U<&&Wnp<B=JfZAyXkXL){)A%'
    '0?i}ubYR-'
    'x^y+p7dvXaikhXhz;)1WFK`pm%i;9cdZXu>CYw+sY1~JcQ^nln?w`o`$U9cm2VElE&YPXM5jr#LXpZ~gKn_(5ak29oDA5{;dPS0h'
    'GY6Pv|G9|l{4i;X}2X~zRLIMPDY8o*me(;{78F=j#{A~X}{Geiqk#e!HOi2;-'
    '#Jw;KJeiSa`CF9O^yrJJ{R2h`S|1lC31{4do(={I;#vXd^221{UXE)(t0qPraU2mHr2zF{W7^=gn0db`M9SOf`$7-'
    'Gv=f_sgzpy6bfQ<!d<QoPrdeqi%uB{mS(N<7Q6>z`>28KexnM_GpLgWhY?z$?o9jYC=e%*inFAm=37!i@?8U>-'
    'XO!!PYRT=mFhc|WZe5k|FzRH^Ud?<m$RAk`-UQ{=kJXm=i_`YX`7-'
    'h7X@5Sj&PtGp2MsA_p<icZG>#_&mi85&09bg{nUn?o{_X3>U;g;%>(_rQaI!Gaz=d<yM;(o?v*v3@7CHSsDJu_;V&wq#VP{qf>*u'
    '5zx^8&ep(fs!LrSFPiv<H=$w{s%43sf;Re%{7X|Fic%AHVNACYq9>@*pOGiLC{T*mNQ5dR-'
    '&84^X$zF}KV_tz5gV^rTle<zG_FvOMG+8EeSXD7(@EbGQDD-Q{T2L0qL8s2h@?-'
    'HFyM~r}%T9r@$git6VX8LTSi(qq2hh^@uP0stHjV(>qO<NjgRmH%!FF$|$_T@RJA&lJ>E}HZ^PA#@k3xZ55iPjgw39I1N&z=(7zy'
    'Ob~(Sem~RhTuT%V7X|2HtN3bxkC|V7M{*$i>w(E5U~4aL>iG0MXGBF%un!^xz=JAVD#BVE!O~FzXu+5y%}~RDh~Phh<1@y()1^hx'
    '0F##RAFNZ)2m!NH1%Q{P!QU7qL<RgaHvv+@ij33Z{2hdRI(qEt)un@dovxVxf)zox#yuyINVJQfFdvg#Qqerx-'
    's4idZD#QS7U@+*d+C@`Duci<!n$(9#?GF4TL!6rie5QUz4<S}hf&(ingyW{NweVC9+r1-'
    ')9@7@K05S4T|(OM|9Bm#YthA*h^h*r&cE7-=n>kb2C1lzYNr>I-'
    'UgWC{Zp01I;KV?=6k<i|O~i?mJG<EFy9jd=|msWl*eZF?Mo1eCixwm#k1g|Rqbxy3<_WhNM2=)*F0&iXjv$Q6!UL5PxWqIk+Xj}s'
    'hr0cOOKuo2M5Wk#}bVy5h5Y?gw|<PtWf#;L%3PEnjdz<TuWim7Rl5E3ASeBD@|e<B9?$cY!0!2Yb^!v16@KsJDlliFSlQfn-'
    'X8rNn;z2Wr6g7VsOvy!MbEh!aIl@w7k@@c$9CD@RVQrKx7sv}Zjx(SyiG_4TlRCe<@H7t`{xWy6Fq;VIoUkBig<kBlIt5Y~3{i)K'
    'X6kMJdHb=D%X8?GRU|~`NCVoL{%}RRmBP`&Eh>lexxPd@xx|k!3V}qa5v7T+uH%jkmGz;^R5aDUSWylh%6s=6fGpY_2YOub`0g{o'
    'Fj~8AM6smF0G%|x%p5l~R(f`VmD+3^PMIn+tS;U#-kCzf`0-'
    'dRt0y4KFmm|Bxc!U>txSUDGz;cH^>69vyT{dQICwW|M@S^oD%xtH?sS9D`vstlqk>QtOFttNv#B4<T&?ks%DY|w@Jq?L*@+Kw*R!'
    'NbQjzbznVSvaK3rqBYQ&&^0+@uW*(_2ao0(gBGFz<x9iNJ)rQVOpDlY>fx+s7Wnssc|rASE1sU(PegaBLSHBF3a*Ckzn>HG~o}_{'
    'Qohm%sa1VHbmx3G5yHQ0s4x-gBvpxXg|^bnq%GU1XB-'
    'MnE;?aD5VMt+<YiBO_A9LO$hc7x?TRWRhqau=&e6@AdVJqqgw*W@(qQ%%Hsz#o2Vk>}0}gCij$YbA4WvQ>@A|7ap@3>kS-tm9^#2'
    'z#hjtsucf>!*3gd#aUhnRgs+DGgjAjJ!d9MpcWm7RJkOPvp&?iki-'
    'i`&IJ+Dq$+4L4}?JX**K3iGVgYZ8dPOZxDgd{QptntgJEH8aFm4wvk;m0RZPWbdjZ$-'
    'iottR;XLzWQs@;nno6J+&Y;=}cPkJzk_z`?26$OA4jtVPp%@nl6ERWRYPu^*kc#yl8ei_4N~4t$NUg$$+uMnpU%^|!qKUp(IW`Y`'
    '%gBkT{`EAuBgkLJZB#C+*{cev$eHr`6l%uf9%S)es>1q2eRQFkRHRxr5Y5_d+|P)|tbEGITL@%YdSnpG7B^@u5|H$rwnP?;JaD_5'
    '?;z?B0xg4xx?UVkcaJv+wlP;B`y@SHzOIN8LzTx{Wi7s&GX7JujO<2WrM9@563f92WapVoMk^Z#Ae-'
    'A45OqB^w3=`=+=UIDr>y@Ql6wd!_42qAXJvViSp|!*Zo(U~%cki;RLHI1=}s9|fif;yc9jG~`rt_^SzgK2MBZ(!*CPoys7{#%Dip'
    'F0_J2pJ=;vthk9XiRQ;!Bp;j@Qkv5!pQ25@dN(J*ifM0UoDbtHOC!7;NyDxRXU$Ypc1&6LBGKqt%k<5!BrGpwcv8?-'
    'D52{OyK@jgD;FHf}{&9Z*##AGJ+RdI+RArq!ANVu5ngR#^nIq`c?;t^D31uFt)TL`c&_OUGRS*Plv{F8Aybwj}-'
    'yEDHC3HiZ7jbUj}b)K=Aa$V7TO9`~H!-'
    '&MMTrt%Yk%Om#KKr=QR58a_8(?@);pWF)GnK2HBg&)>iNkzx4pNRN*HPy}WdJ$WTh^?KjcnVerv*!pqN8?@!hY!V%+!f;BBqcy6T'
    '=U;RIuhWb*p$zj{{#|<rnk8z?_82wTu7%;H0vp*#fyu_wrmmM$-'
    'vsVAgKQmCcxaTN;<p@0ie`x3t)|sWMeYlj&UJ%jI~g4k_nnk%#t36TUSF22kQb<!4b?6G}HyL6?~<E?^Z<Da~X5X+wqPOb#YQR4$'
    'YY?#IlH!WXHukSt^#iUU$!Pf+}ey`%&MTJ;DdY^)m9hrXC|n<aAXz!90LOc#RG<0znsMYW_r!iEfO2hW`NIw5$q<*^thKld^dsj?'
    'D!l{r5SznWRK5k8ii@c%50ZncLzx;qd7wA|vJz&Y#!6gZV<w6&lXDxK6$Ld-'
    '3gNwI=r;V3*WyH}w*T1Z!g01A&FO_h)9N+!E{H<wICMH%qtj^d?UghFf@V-'
    '6J{N$N|s{9qT@P<RD>R3bvNZ}A&z9gF1xgj3hKtDLc1J%%#+IHE?JwwlO>-V2|zF(yHsT-Rc!Z7%d+ry|^!lxiVQvQnQ?0l4`sy%'
    '=(xn|E-'
    '|XPj_bz18NJiuv69Jg29E7tM~$BBX7s4S%s|Bi^u+Ch=mI+&hw_bITMcE!&v1^)UN{!nD=HA?x+|RmPBMh3>$%XX3rHC4A1_8*y1'
    '&=*7HWE_Wkb27_Ms1{3P7(ibT1A`!1Xk%%`v2pfeEcTDAO#~{;FpDamAc!GD7)x}LMi^gZb=IU@Got{au6^CC^A6BR=KXDbPL_rl'
    'Zol4`{Z>}Y}c+Yff5zqDLL{#F|nlH&D>iaNamTEuYrLr<!M!EN=AAelkoLT3MJ)^o#7jKM2OD}p?qVL;Rx*HS8<xG9@MRPpy6n;)'
    '=7v-<uuB{x(`IX@5&K6>#?<<*=b&BxhuIsUgsLnu<4VeQKFCo%c1^1RhBI}OUL0oFWF=J*F`O#l#ga>xfH~am-'
    '!=s|YwZ1y4mQ>~ne1m^D-vyW!8ub=3z>f-'
    'V)kBaNEc}=WqDhP!3qc9#>(lGg$<#Hg+SpMaTW(oetmM)vOz~zDJtT4cj>Ah%lxoG~QBvWC@Ib9glO+~~Q8{W6njaEm`X{<4ZTOV'
    '<i$J0}W$G)EVn^~{NOPA|c#3yqE=$_@Sc@dek!wrwe_-'
    '`y1Et>uf1x}u<$#P@E5iP^6gFs;Nxpwo*_8EDCct=rIc$uL%+5?wppC!G4QB0-'
    '&?adfq>`Lpba?#YI^>ySQ&!J~uUL9<@e75eA4?F}9hWkjnW%{5c1Lyd_;@&ekbRhcf(5s40w#^C5FwKe5E!g+3t=nc(+%%Q`IfA%'
    '_k6CokmdDrLRD2=DmUuLL9u{Newj&zpnw3XUPj15d>?p^T^fUc%>ao2aZ>rNvNA{U&#zJy2p57cyHJMRK26Lh{n_DhYxv*a0cec{'
    'MLIX*yVEx1{@GR6JEpmrCeW9c@YiY$9k_w$*@6A>RLvgH7YReQ4nH-9J~K7-QU|sA#Bp2_YkZ-'
    '%RL6D1lInM;?iATe<q86Bc^5S?VOFUdX(6<kHD{5G&Mm^$`=i-'
    '}cdzDfyPumd*==VBhtaJBP|Yy?nrq{~MYoDB2vK><onUhtrAkYWo#tKhtK=7`TBAT_*w|o99G~esEf*_G*FDFOaRfh?E^XsewlX('
    'MI4Qi$BzgO|jFC3#gQEoc)5=cX@gjFAzvdjmbnHL@7OGYn(f+!RLm%hX1h3*wpFH)>>2Cs>De1Vl(}mNlyy|2!g^I4~5ATX@mbqB'
    '}a$LbpyZg8)R1qFcKqQ1qs4IRlM*tA_q(-Ll><Zb!e4*ePe?|U?dpE{O1LC}{-'
    'H$8Vy!c2ofxo_??e9WVu4<=|9F&NLAzKNj(6Bixx~5B+M8Mg<bj&B#K<ur|pK@%r^RVov`eY>)%1U5*eU-'
    'T>MI&k^+OqoAzVvffnm+qE(D0UH6^Iromj&BX0?%_84v~ZU@BaX^cU;K'
    )
)).decode("utf-8"))

_SELLABLE = (
    "STRAWBERRY", "MELON", "MILK", "WOOL", "EGG",
    "TOMATO", "CARROT", "WHEAT", "FERTILIZER",
)
_PRODUCT_BY_ANIMAL = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
_GLUT_WEIGHT = {
    "STRAWBERRY": 2.0, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}
_STATE = {0: {}, 1: {}}
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8
_PREEMPT_LEAD = 1
# The public v21 notebook used 0.55.  On live executable public-opponent
# checks, repeated preemption was consistently worse than preserving the
# route's scheduled SELLs, so v21.1 disables that optional intervention while
# retaining the route, weed recovery, and terminal liquidation safeguards.
_PREEMPT_THRESHOLD = 2.0
_PREEMPT_FRACTION = 0.5
_PREEMPT_MAX_BATCH = 30
_PREEMPT_COOLDOWN = 8
_PREEMPT_START = 24
_PREEMPT_STOP = 680
_PREEMPT_MAX_CLONE_DISTANCE = 2


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


def _align_hands(action, obs):
    action = _copy_action(action)
    seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
    farms = list(_get(obs, "farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    expected = len(_get(farm, "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
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
    """Actor-local DIG -> retry -> bounded catch-up transaction."""
    action = _align_hands(action, obs)
    seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
    game = _WEED_STATE[seat]
    if step == 0 or step < game.get("last_step", -1):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farms = list(_get(obs, "farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
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


def _shed_access(size):
    half = size // 2
    return {
        (half - 1, half - 1), (half, half - 1),
        (half - 1, half), (half, half),
    }


def _projected_shed(obs, action):
    seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
    farms = list(_get(obs, "farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    private = _get(obs, "private", {}) or {}
    projected = {
        key: max(0, int(value or 0))
        for key, value in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = list(_get(private, "inventories", []) or [])
    positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles = list(_get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        if tiles[y][x] == "LOCKED" or not isinstance(unit_action, list) or not unit_action:
            continue
        inventory = {
            key: max(0, int(value or 0))
            for key, value in dict(inventories[index] or {}).items()
        }
        if unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if (
                structure is not None and isinstance(tile, dict)
                and tile.get("kind") == structure and "animal" not in tile
            ):
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
    counts = {
        key: 0 for key in (
            "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED",
        )
    }
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
        return math.inf
    left, right = _public_signature(farms[0]), _public_signature(farms[1])
    return (
        abs(left[0] - right[0])
        + 3 * abs(left[1] - right[1])
        + sum(abs(a - b) for a, b in zip(left[2], right[2]))
    )


def _safe_market(obs, action):
    action = _align_hands(action, obs)
    remaining = _projected_shed(obs, action)
    market = []
    for raw in action.get("market", []) or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL":
            item = order[1]
            try:
                requested = max(0, int(order[2]))
            except (TypeError, ValueError):
                requested = 0
            quantity = min(requested, max(0, int(remaining.get(item, 0) or 0)))
            if quantity <= 0:
                continue
            order[2] = quantity
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - quantity)
        market.append(order)
    action["market"] = market[:10]
    return action


def _preempt_action(obs, action, step):
    seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
    state = _STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "last_preempt": -10**9}
        _STATE[seat] = state
    state["last_step"] = step
    if not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    if step - int(state.get("last_preempt", -10**9)) < _PREEMPT_COOLDOWN:
        return action
    if _clone_distance(obs) > _PREEMPT_MAX_CLONE_DISTANCE:
        return action
    future = [
        row for row in _HAZARD.get(str(step + _PREEMPT_LEAD), [])
        if float(row[1]) >= _PREEMPT_THRESHOLD
    ]
    if not future:
        return action
    action = _safe_market(obs, action)
    existing = list(action.get("market") or [])
    room = 10 - len(existing)
    if room <= 0:
        return action
    existing_items = {
        order[1] for order in existing
        if len(order) >= 3 and order[0] == "SELL"
    }
    shed = _projected_shed(obs, action)
    new_orders = []
    for item, _probability, median_quantity in future:
        if room <= 0 or item in existing_items:
            continue
        quantity = min(
            max(0, int(shed.get(item, 0) or 0)),
            _PREEMPT_MAX_BATCH,
            max(1, int(round(float(median_quantity) * _PREEMPT_FRACTION))),
        )
        if quantity <= 0:
            continue
        new_orders.append(["SELL", item, quantity])
        room -= 1
    if new_orders:
        action["market"] = new_orders + existing
        state["last_preempt"] = step
    return action


def _opponent_exposure(obs):
    seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
    farms = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    exposure = {item: 0.0 for item in _SELLABLE}
    for row in (_get(opponent, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop = str(tile.get("crop", "")).upper()
            if crop in exposure:
                exposure[crop] += max(1.0, float(tile.get("yield_units", 0) or 0))
            product = _PRODUCT_BY_ANIMAL.get(str(tile.get("animal", "")).upper())
            if product:
                exposure[product] += 1.0 + max(0.0, float(tile.get("yield_units", 0) or 0))
            if tile.get("fertilizer_available", False):
                exposure["FERTILIZER"] += 1.0
    return exposure


def _terminal_market(obs, action):
    action = _align_hands(action, obs)
    shed = _projected_shed(obs, action)
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    exposure = _opponent_exposure(obs)
    rows = []
    for index, item in enumerate(_SELLABLE):
        quantity = max(0, int(shed.get(item, 0) or 0))
        if quantity <= 0:
            continue
        score = (
            (1.0 + exposure.get(item, 0.0))
            * _GLUT_WEIGHT.get(item, 1.0)
            * max(1.0, float(prices.get(item, 1) or 1))
            * math.log1p(quantity)
        )
        rows.append((score, -index, item, quantity))
    rows.sort(reverse=True)
    action["market"] = [
        ["SELL", item, quantity] for _, _, item, quantity in rows[:10]
    ]
    return action


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _safe_market(obs, action)
        action = _preempt_action(obs, action, step)
        if step == 718:
            action = _terminal_market(obs, action)
        return _align_hands(action, obs)
    except Exception:
        seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs):
    return agent(obs)
