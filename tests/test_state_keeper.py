from pandamonium.state_server import SimpleStateKeeper as SimpleStateKeeperBase


class SimpleStateKeeper(SimpleStateKeeperBase):
    def emit_create_dobject_view(self, recipients, dobject_ids):
        pass

    def emit_destroy_dobject_view(self, recipients, dobject_ids):
        pass


def test_basics():
    client = 0
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])


def test_set_interest_in_empty_zone():
    client = 0
    zone = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)

    new_dobjects = sk.set_interest(client, zone)
    assert new_dobjects == set()


def test_unset_interest_in_empty_zone():
    client = 0
    zone = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)

    new_dobjects = sk.set_interest(client, zone)
    lost_dobjects = sk.unset_interest(client, zone)
    assert lost_dobjects == set()


def test_add_presence_in_empty_zone():
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    new_recipients = sk.add_presence(dobject, zone)
    assert new_recipients == set()


def test_remove_presence_from_empty_zone():
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    new_recipients = sk.add_presence(dobject, zone)
    lost_recipients = sk.remove_presence(dobject, zone)
    assert lost_recipients == set()


def test_set_interest_in_full_zone():
    client = 0
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    sk.add_presence(dobject, zone)
    new_dobjects = sk.set_interest(client, zone)
    assert new_dobjects == set([dobject])


def test_unset_interest_in_full_zone():
    client = 0
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    sk.add_presence(dobject, zone)
    sk.set_interest(client, zone)
    lost_dobjects = sk.unset_interest(client, zone)
    assert lost_dobjects == set([dobject])


def test_add_presence_in_full_zone():
    client = 0
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    sk.set_interest(client, zone)
    new_recipients = sk.add_presence(dobject, zone)
    assert new_recipients == set([client])


def test_remove_presence_from_full_zone():
    client = 0
    zone = 0
    dobject = 0
    sk = SimpleStateKeeper()
    sk.create_recipient(client)
    sk.create_zone(zone)
    sk.create_dobject(dobject, None, [])

    sk.set_interest(client, zone)
    sk.add_presence(dobject, zone)
    lost_recipients = sk.remove_presence(dobject, zone)
    assert lost_recipients == set([client])




# TODO: Test complex x-seen-by-y relations
