import itertools

# --- CONSTANTES GLOBALES ---
COLS = "ABCDEFGHI"  # Columnas del tablero
ROWS = range(1, 10)  # Filas del tablero


def clear_board():
    """
    Inicializa el tablero con todos los valores posibles (1 a 9) en cada celda.

    Returns:
        dict: Diccionario con celdas como claves y sets de valores posibles como valores.
    """
    print("Inicializando el tablero...")
    return {f"{col}{row}": set(range(1, 10)) for row in ROWS for col in COLS}


def load_board(filename):
    """
    Carga las restricciones y el tablero desde un archivo.

    Args:
        filename (str): Nombre del archivo que contiene las restricciones.

    Returns:
        tuple: Diccionario del tablero y lista de restricciones.
    """
    vars = clear_board()
    constraints = []

    print(f"Cargando el tablero desde el archivo: {filename}")
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip().upper()
            if line and ':' in line:
                print(f"Procesando línea: {line}")
                parts = line.split(':')
                if ',' in parts[1]:
                    sum_value, cells = int(parts[0]), parts[1].split(',')
                    constraints.append((sum_value, cells))
                else:
                    value, cell = int(parts[0]), parts[1]
                    vars[cell] = {value}
                    print(f"Valor fijo asignado: {cell} = {value}")
            else:
                print(f"Línea ignorada: {line}")

    return vars, constraints


def propagate_constraints(vars, constraints):
    """
    Propaga las restricciones iniciales para reducir los dominios posibles de cada celda.

    Args:
        vars (dict): Tablero con dominios de cada celda.
        constraints (list): Lista de restricciones de suma.
    """
    print("Propagando restricciones iniciales...")
    changes = True
    while changes:
        changes = False
        for sum_value, cells in constraints:
            possible_combinations = [
                comb for comb in itertools.product(*(vars[cell] for cell in cells))
                if sum(comb) == sum_value and len(set(comb)) == len(comb)
            ]
            for i, cell in enumerate(cells):
                possible_values = set(comb[i] for comb in possible_combinations)
                old_domain = vars[cell].copy()
                vars[cell] &= possible_values
                if vars[cell] != old_domain:
                    changes = True
                    print(f"Celda {cell} dominio reducido a {vars[cell]}.")


def is_valid_assignment(vars, var, value, constraints):
    """
    Comprueba si asignar un valor a una celda es válido según las restricciones.

    Args:
        vars (dict): Tablero con dominios de cada celda.
        var (str): Celda a evaluar.
        value (int): Valor que se quiere asignar.
        constraints (list): Lista de restricciones de suma.

    Returns:
        bool: True si la asignación es válida, False en caso contrario.
    """
    for sum_value, cells in constraints:
        if var in cells:
            current_sum = sum(next(iter(vars[cell])) for cell in cells if len(vars[cell]) == 1)
            remaining_cells = len([cell for cell in cells if len(vars[cell]) > 1])
            if current_sum + value > sum_value or (remaining_cells == 1 and current_sum + value != sum_value):
                return False
    return True


def is_solved(vars):
    """
    Comprueba si todas las celdas tienen un único valor asignado.

    Args:
        vars (dict): Tablero con dominios de cada celda.

    Returns:
        bool: True si todas las celdas tienen un único valor, False en caso contrario.
    """
    return all(len(vars[cell]) == 1 for cell in vars)


def select_unassigned_variable(vars):
    """
    Selecciona una celda con más de un posible valor.

    Args:
        vars (dict): Tablero con dominios de cada celda.

    Returns:
        str: La celda seleccionada, o None si no hay celdas sin asignar.
    """
    for cell in vars:
        if len(vars[cell]) > 1:
            return cell
    return None


def solve_kakuro(vars, constraints):
    """
    Resuelve el tablero de Kakuro usando backtracking.

    Args:
        vars (dict): Tablero con dominios de cada celda.
        constraints (list): Lista de restricciones de suma.

    Returns:
        bool: True si el tablero se resuelve, False en caso contrario.
    """
    if is_solved(vars):
        return True

    var = select_unassigned_variable(vars)
    if not var:
        return False

    domain = vars[var].copy()
    for value in domain:
        if is_valid_assignment(vars, var, value, constraints):
            vars[var] = {value}
            if solve_kakuro(vars, constraints):
                return True
            vars[var] = domain  # Backtrack

    return False


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    filename = 'board.txt'

    # Cargar el tablero y las restricciones
    vars, constraints = load_board(filename)

    # Propagar restricciones iniciales
    propagate_constraints(vars, constraints)

    # Mostrar tablero tras aplicar restricciones iniciales
    print("Tablero después de aplicar restricciones iniciales:")
    for row in ROWS:
        print(" ".join("".join(map(str, vars[f"{col}{row}"])) for col in COLS))

    # Intentar resolver el Kakuro
    if solve_kakuro(vars, constraints):
        print("Tablero resuelto:")
        for row in ROWS:
            print(" ".join(str(next(iter(vars[f'{col}{row}']))) for col in COLS))
    else:
        print("No se encontró solución.")
