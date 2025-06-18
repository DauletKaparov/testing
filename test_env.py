import sys
import site
import pkg_resources

def main():
    print("Python executable:", sys.executable)
    print("\nPython path:")
    for p in sys.path:
        print(f" - {p}")
    
    print("\nInstalled packages:")
    for pkg in sorted([f"{p.key}=={p.version}" for p in pkg_resources.working_set]):
        print(f" - {pkg}")

if __name__ == "__main__":
    main()
