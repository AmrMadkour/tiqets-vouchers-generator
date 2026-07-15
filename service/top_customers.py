from collections import defaultdict


def top_5_customers(grouped):
    ticket_counts = defaultdict(int)
    for (customer_id, order_id), barcodes in grouped.items():
        ticket_counts[customer_id] += len(barcodes)

    ranked = sorted(ticket_counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:5]
