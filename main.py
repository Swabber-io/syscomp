import subprocess

def main():
    print("bird boop poop")
    subprocess.run(["sudo", "ls", "-l"])

if __name__ == "__main__":
    main()