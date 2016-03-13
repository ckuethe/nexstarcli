#!/usr/bin/env python
import nexstar
import argparse


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", help="Port telescope is connected to. Default = /dev/ttyUSB0")
    group.add_argument("--get_azel", action="store_true")
    group.add_argument("--get_location", action="store_true")
    group.add_argument("--get_model", action="store_true")
    group.add_argument("--get_radec", action="store_true")
    group.add_argument("--get_time", action="store_true")
    group.add_argument("--get_tracking_mode", action="store_true")
    group.add_argument("--get_version", action="store_true")
    group.add_argument("--set_location", nargs=2, metavar=("latitude", "longitude"))
    group.add_argument("--goto_azel", nargs=2, metavar=("az", "el"))
    group.add_argument("--goto_in_progress", action="store_true")
    group.add_argument("--goto_radec", nargs=2, metavar=("Ra", "Dec"))
    group.add_argument("--set_tracking_mode", metavar="tracking_mode")
    group.add_argument("--set_time")
    group.add_argument("--cancel_goto", action="store_true")
    group.add_argument("--alignment_complete", action="store_true")
    group.add_argument("--echo")
    group.add_argument("--slew_fixed", nargs=2, metavar=("az_rate", "el_rate"))
    group.add_argument("--slew_var", nargs=2, metavar=("az_rate", "el_rate"))
    group.add_argument("--sync", nargs=2, metavar=("ra", "dec"))

    args = parser.parse_args()

    if args.d:
        device = args.d
    else:
        device = '/dev/ttyUSB0'

    telescope = nexstar.NexStar(device)

    if args.get_azel:
        print(telescope.get_azel())
    elif args.get_location:
        print(telescope.get_location())
    elif args.get_radec:
        print(telescope.get_radec())
    elif args.get_tracking_mode:
        print(telescope.get_tracking_mode())
    elif args.get_version:
        print(telescope.get_version())
    elif args.get_time:
        print(telescope.get_time())
    elif args.set_location:
        latitude = args.set_location[0]
        longitude = args.set_location[1]
        telescope.set_location(
            map(int, longitude.split(",")),
            map(int, latitude.split(","))
        )
    elif args.set_time:
        telescope.set_time(map(int, args.set_time.split(",")))
    elif args.set_tracking_mode:
        telescope.set_tracking_mode(int(args.set_tracking_mode))
    elif args.goto_azel:
        _az = float(args.goto_azel[0])
        _el = float(args.goto_azel[1])
        telescope.goto_azel(_az, _el)
    elif args.goto_in_progress:
        if telescope.goto_in_progress():
            print("Yes")
        else:
            print("No")
    elif args.goto_radec:
        _ra = float(args.goto_radec[0])
        _dec = float(args.goto_radec[1])
        telescope.goto_radec(_ra, _dec)
    elif args.alignment_complete:
        if telescope.alignment_complete():
            print("Yes")
        else:
            print("No")
    elif args.cancel_goto:
        telescope.cancel_goto()
    elif args.echo:
        telescope.echo(args.echo)
    elif args.slew_fixed:
        _az_rate = float(args.slew_fixed[0])
        _el_rate = float(args.slew_fixed[1])
        telescope.slew_fixed(_az_rate, _el_rate)
    elif args.slew_var:
        _az_rate = float(args.slew_var[0])
        _el_rate = float(args.slew_var[1])
        telescope.slew_var(_az_rate, _el_rate)
    elif args.sync:
        _ra = float(args.sync[0])
        _dec = float(args.sync[1])
        telescope.sync(_ra, _dec)
    else:
        print(parser.print_help())


if __name__ == '__main__':
    main()
