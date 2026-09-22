from fire import Fire
from src.UserCLI import UserCLI

if __name__ == '__main__':
    # Fire(UserCLI)
    try:
        Fire(UserCLI)
    except Exception as e:
        print(f'Error: {e}')
