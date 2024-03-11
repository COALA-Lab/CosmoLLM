#!python3

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(description="Process node configuration.")

    parser.add_argument("count", type=int, help="Enter node count")
    parser.add_argument("image", type=str, help="Enter image")

    parser.add_argument("-c", "--cpu_count", type=int, default=2, help="Node CPU count")
    parser.add_argument(
        "-m", "--ram_size_mib", type=int, default=4096, help="Node RAM allocation"
    )
    parser.add_argument("-e", "--env", nargs='+', help="List of environment variables (e.g., KEY=VALUE)")
    parser.add_argument("--name", type=str, help="Node name")

    args = parser.parse_args()

    count = args.count
    image = args.image
    cpu_count = args.cpu_count
    ram_size_mib = args.ram_size_mib
    env = args.env
    name = args.name

    node_ips = []

    for i in range(count):
        if not name:
            image_slug = image.replace(":", "_").replace("/", "_")
            node_name = f"{image_slug}_{i}"
        else:
            node_name = f"{name}_{i}"

        env_params = []
        if env:
            for e in env:
                env_params.append("-e")
                env_params.append(e)

        subprocess.run(
            ["docker", "rm", node_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        subprocess.run([
            "docker", "run", "-d",
            f"--cpus={cpu_count}",
            f"-m={ram_size_mib}MiB",
            f"--name={node_name}",
            *env_params,
            f"{image}"
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"Node {node_name} started")

        node_ip = subprocess.run(
            ["docker", "inspect", "--format", "{{.NetworkSettings.IPAddress}}", node_name],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ).stdout.strip()

        node_ips.append(node_ip.decode("utf-8"))

    print(f"Node IPs: {node_ips}")


if __name__ == "__main__":
    main()
