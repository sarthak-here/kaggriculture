import sys, importlib.util, math
sys.path.insert(0, '.')
import game_data as gd

spec = importlib.util.spec_from_file_location("pub", "submit_pub/main.py")
pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(pub)

print(f"{'item':<11}{'deficit':>8}{'true$':>9}{'pub$':>9}{'err%':>8}")
for item in ("CARROT","TOMATO","EGG"):
    T = gd.MARKET_PARAMS[item]["T"]
    for frac in (0.25, 0.5, 0.9, 1.0, 1.25, 1.5, 2.0):
        d = int(T*frac)
        inv = 10000 - d
        true = gd.predicted_price(item, inv)
        p = pub._market_price(item, inv)
        print(f"{item:<11}{d:>8}{true:>9}{p:>9}{100*(p-true)/true:>7.0f}%")
    print()

# impact-ranking consequence: selling 20 units at a spike
print("=== impact score error, selling 20u past the knee ===")
for item in ("CARROT","TOMATO","EGG"):
    T = gd.MARKET_PARAMS[item]["T"]
    inv = 10000 - int(T*1.5)
    q = 20
    true_now, true_later = gd.predicted_price(item, inv), gd.predicted_price(item, inv+q)
    pub_now, pub_later = pub._market_price(item,inv), pub._market_price(item,inv+q)
    print(f"{item:<11} true impact {q*(true_now-true_later):>9,.0f}   pub thinks {q*(true_now-pub_later):>9,.0f}  (uses real quote now, model later)")
