from sw_nebula_service.create_schemas import main as create_full_schemas
from sw_nebula_service.insert_nodes import main as insert_directory_nodes


def main():
    create_full_schemas()
    insert_directory_nodes()


if __name__ == "__main__":
    main()
