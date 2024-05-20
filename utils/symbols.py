
def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]