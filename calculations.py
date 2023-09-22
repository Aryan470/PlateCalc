KG_LB_COEFF = 2.20462


def kg_to_lb(kg):
    return round(kg * KG_LB_COEFF)


def lb_to_kg(lb):
    return round(lb / KG_LB_COEFF)


def get_plate_counts(weight, units, interface):
    input_unit = units[0]
    output_unit = units[1]

    # multiply by 100 so we can use 100ths
    weight *= 100

    # convert mismatched units
    if input_unit != output_unit:
        if input_unit == "KG":
            weight = kg_to_lb(weight)
        else:
            weight = lb_to_kg(weight)

    BAR_WEIGHT = interface.config_read("weights")[output_unit]["bar"]
    COLLAR_WEIGHT = interface.config_read("weights")[output_unit]["collar"]
    plate_list = interface.config_read("weights")[output_unit]["plates"]

    # subtract the weight of the bar
    weight -= BAR_WEIGHT * 100

    # split to two sides
    weight //= 2

    # we have < bar weight, so just leave it as 0
    if weight < COLLAR_WEIGHT:
        return [], (BAR_WEIGHT) * 100

    # subtract weight of one collar on each side
    weight -= COLLAR_WEIGHT

    # use biggest plates first
    used_plates = sorted(
        [
            (plate, value["value"])
            for plate, value in plate_list.items()
            if value["using"]
        ],
        reverse=True,
        key=lambda x: x[1],
    )

    weight = ((weight + used_plates[-1][1] // 2) // used_plates[-1][1]) * used_plates[
        -1
    ][1]
    counts = []

    end_weight = 0
    for i in range(len(used_plates)):
        # get the count of this plate we can use
        count = weight // used_plates[i][1]
        # reduce the weight by the appropriate amount
        weight -= count * used_plates[i][1]

        if count > 0:
            counts.append((count, used_plates[i][0]))
            end_weight += used_plates[i][1] * count

    end_weight *= 2
    end_weight += BAR_WEIGHT * 100
    end_weight += COLLAR_WEIGHT * 2
    return counts, end_weight


def format_hundredths_weight(weight):
    if weight % 100 == 0:
        return str(weight // 100)
    elif weight % 10 == 0:
        return "%d.%d" % (weight // 100, weight % 100 // 10)

    return "%d.%d" % (weight // 100, weight % 100)


def get_plate_count_strings(counts):
    return ["{label}x{qty}".format(label=count[1], qty=count[0]) for count in counts]
