# ==============================================
# Algorithm 3.1 – Basic Counting
# ==============================================
def algorithm_3_1(sequence, k):
    n = 0
    T = set()
    c = {}
    for i in sequence:
        n += 1
        if i in T:
            c[i] += 1
        elif len(T) < k - 1:
            T.add(i)
            c[i] = 1
        else:
            for j in list(T):
                c[j] -= 1
                if c[j] == 0:
                    T.remove(j)
                    del c[j]
    return T, c


# ==============================================
# Algorithm 3.2 – Delta-Based Normalization
# ==============================================
def algorithm_3_2(sequence, k):
    n = 0
    Δ = 0
    T = set()
    c = {}
    for i in sequence:
        n += 1
        if i in T:
            c[i] += 1
        else:
            T.add(i)
            c[i] = 1 + Δ

        if n // k != Δ:
            Δ = n // k
            for j in list(T):
                if c[j] < Δ:
                    T.remove(j)
                    del c[j]
    return T, c


# ==============================================
# Algorithm 3.3 – Replacement by Minimum Counter
# ==============================================
def algorithm_3_3(sequence, k):
    n = 0
    T = set()
    c = {}
    for i in sequence:
        n += 1
        if i in T:
            c[i] += 1
        elif len(T) < k:
            T.add(i)
            c[i] = 1
        else:
            j = min(T, key=lambda x: c[x])
            T.remove(j)
            del c[j]
            T.add(i)
            c[i] = 1
    return T, c


# ==============================================
# Test data: city names
# ==============================================
city_sequence = [
    "Tokyo", "Kyoto", "Osaka", "Tokyo", "Nagoya", "Osaka", "Tokyo",
    "Kyoto", "Shizuoka", "Kyoto", "Osaka", "Tokyo", "Kobe", "Tokyo",
    "Kyoto", "Tokyo", "Hiroshima", "Osaka", "Tokyo", "Kyoto", "Sendai",
    "Tokyo", "Tokyo", "Osaka", "Kyoto", "Nagoya", "Tokyo", "Kyoto",
    "Tokyo", "Osaka", "Tokyo", "Kyoto", "Tokyo", "Tokyo", "Osaka",
    "Kyoto", "Tokyo", "Nagoya", "Tokyo", "Kyoto", "Osaka", "Tokyo",
    "Fukuoka", "Tokyo", "Kyoto", "Tokyo", "Sapporo", "Kyoto", "Osaka",
    "Tokyo", "Kyoto", "Tokyo", "Osaka", "Kyoto", "Tokyo", "Nagoya",
    "Tokyo", "Kyoto", "Osaka", "Tokyo", "Tokyo", "Kyoto", "Tokyo",
    "Tokyo", "Osaka", "Tokyo", "Kyoto"
]

k = 3  # kapasitas maksimum

# ==============================================
# Run and show results
# ==============================================
if __name__ == "__main__":
    print("Total data:", len(city_sequence))
    print("Unique cities:", len(set(city_sequence)))
    print("=" * 60)

    result1 = algorithm_3_1(city_sequence, k)
    result2 = algorithm_3_2(city_sequence, k)
    result3 = algorithm_3_3(city_sequence, k)

    print("Algorithm 3.1 result:", result1)
    print("Algorithm 3.2 result:", result2)
    print("Algorithm 3.3 result:", result3)
