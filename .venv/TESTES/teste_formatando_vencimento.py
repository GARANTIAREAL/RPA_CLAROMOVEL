data_vencimento = "28-06-2024"

calendario = [(1, "jan"), (2, "fev"), (3, "mar"), (4, "abr"), (5, "mai"), (6, "jun"), (7, "jul"), (8, "ago"), (9, "set"), (10, "out"), (11, "nov"), (12, "dez")]

mes_vencimento_nota = int(data_vencimento.split('-')[1])
ano_vencimento_nota = int(data_vencimento.split('-')[2])
dia_vencimento_nota = str(data_vencimento.split('-')[0])

print(mes_vencimento_nota)
print(ano_vencimento_nota)
print(dia_vencimento_nota)

for m in calendario:
    if m[0] == mes_vencimento_nota:
        mes_vencimento_nota = m[1]
        print(mes_vencimento_nota)


dia = str('09')
dia = dia.strip('0')
print(dia)


valor_total = '1.300,25'
valor_total = valor_total.replace('.', '')
valor_total = valor_total.replace(',', '.')
print(valor_total)
valor_total = valor_total.replace('.', ',')
print(valor_total)

