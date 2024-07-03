import re
from rest_framework.routers import Route, DynamicRoute, SimpleRouter, flatten
from django.core.exceptions import ImproperlyConfigured


class CustomRouter(SimpleRouter):

    routes = [
        Route(
            url=r"^{prefix}/$",
            mapping={"get": "list"},
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        Route(
            url=r"^{prefix}/create/$",
            mapping={"post": "create"},
            name="{basename}-create",
            detail=False,
            initkwargs={"suffix": "Create"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/$",
            mapping={"get": "retrieve"},
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Detail"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/update/$",
            mapping={"patch": "partial_update"},
            name="{basename}-update",
            detail=True,
            initkwargs={"suffix": "Update"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/delete/$",
            mapping={"delete": "destroy"},
            name="{basename}-delete",
            detail=True,
            initkwargs={"suffix": "Delete"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{url_path}/$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
        DynamicRoute(
            url=r"^{prefix}/{url_path}/$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
    ]

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """
        # converting to list as iterables are good for one pass, known host needs to be checked again and again for
        # different functions.
        known_actions = list(
            flatten(
                [
                    route.mapping.values()
                    for route in self.routes
                    if isinstance(route, Route)
                ]
            )
        )
        extra_actions = viewset.get_extra_actions()
        # print(known_actions)
        # print([action.__name__ for action in extra_actions])
        handlers = getattr(viewset, "function_handlers", None)

        # checking action names against the known actions list
        not_allowed = [
            action.__name__
            for action in extra_actions
            if action.__name__ in known_actions
        ]
        if not_allowed:
            msg = (
                "Cannot use the @action decorator on the following "
                "methods, as they are existing routes: %s"
            )
            raise ImproperlyConfigured(msg % ", ".join(not_allowed))

        # partition detail and list actions
        detail_actions = [action for action in extra_actions if action.detail]
        list_actions = [action for action in extra_actions if not action.detail]

        routes = []
        for route in self.routes:
            if isinstance(route, DynamicRoute) and route.detail:
                routes += [
                    self._get_dynamic_route(*self._auto_gen_route(route, action))
                    for action in detail_actions
                ]
            elif isinstance(route, DynamicRoute) and not route.detail:
                routes += [
                    self._get_dynamic_route(*self._auto_gen_route(route, action))
                    for action in list_actions
                ]
            else:
                if handlers is not None:
                    add_route = False
                    for name_fun in route.mapping.values():
                        if name_fun in handlers:
                            add_route = True
                            break
                        else:
                            add_route = False
                    if add_route:
                        routes.append(route)
                else:
                    routes.append(route)
        return routes

    def _auto_gen_route(self, route, action):
        pattern = r"(<[str|int]+:[a-zA-Z_-]+>)|(<[pk|slug]+>)"
        match = re.findall(pattern, action.url_path)
        for opt1, opt2 in match:
            if len(opt1):
                url = action.url_path
            if len(opt2) == 4:
                url = action.url_path.replace("<pk>", "{lookup}")
            else:
                url = action.url_path.replace("<slug>", "{trailing_slash}")
        if len(match):
            new_route = DynamicRoute(
                url=route.url.replace("{url_path}", url),
                name=route.name,
                detail=route.detail,
                initkwargs=route.initkwargs.copy(),
            )
            return new_route, action
        return route, action
