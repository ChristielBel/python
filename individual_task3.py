import math

def distribute_seats(parties):
    total_votes = sum(votes for _, votes in parties)
    print(f"1. Общая сумма голосов за все партии: {total_votes}")

    quota = total_votes / 450
    print(f"2. Первое избирательное частное (количество голосов для одного места): {quota}")

    seats = []
    fractional_parts = []
    total_seats_allocated = 0

    print("3. Места, распределенные на основе целой части:")
    for name, votes in parties:
        seat_count = votes // quota
        total_seats_allocated += seat_count
        seats.append(int(seat_count))
        fractional_part = (votes / quota) - seat_count
        fractional_parts.append(fractional_part)

        print(f"   - {name}: {int(seat_count)} мест (целая часть), дробная часть: {fractional_part}")

    remaining_seats = int(450 - total_seats_allocated)
    print(f"4. Оставшиеся места для распределения после первого этапа: {remaining_seats}")

    sorted_parties = sorted(
        enumerate(fractional_parts),
        key=lambda x: (-x[1], -parties[x[0]][1])
    )

    for i in range(remaining_seats):
        index = sorted_parties[i][0]
        seats[index] += 1
        print(f"   - Дополнительное место передано партии: {parties[index][0]}")

    return seats

with open("input.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

parties = []
for line in lines:
    party_name, votes = line.rsplit(maxsplit=1)
    parties.append((party_name, int(votes)))

allocated_seats = distribute_seats(parties)

print("5. Окончательное распределение мест:")
with open("output.txt", "w", encoding="utf-8") as file:
    for i, (party_name, _) in enumerate(parties):
        result = f"{party_name} {allocated_seats[i]}"
        print(result)
        file.write(result + "\n")
