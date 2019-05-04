package com.comp6239.Student;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.widget.GridLayoutManager;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * A fragment representing a list of Items.
 * <p/>
 * Activities containing this fragment MUST implement the {@link OnSearchTutorFragmentInteractionListener}
 * interface.
 */
public class StudentSearchTutorsFragment extends Fragment {

    // TODO: Customize parameter argument names
    private static final String ARG_COLUMN_COUNT = "column-count";
    // TODO: Customize parameters
    private int mColumnCount = 1;
    private OnSearchTutorFragmentInteractionListener mListener;
    private BackendRequestController apiBackend;

    /**
     * Mandatory empty constructor for the fragment manager to instantiate the
     * fragment (e.g. upon screen orientation changes).
     */
    public StudentSearchTutorsFragment() {
    }

    // TODO: Customize parameter initialization
    @SuppressWarnings("unused")
    public static StudentSearchTutorsFragment newInstance(int columnCount) {
        StudentSearchTutorsFragment fragment = new StudentSearchTutorsFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_COLUMN_COUNT, columnCount);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        apiBackend = BackendRequestController.getInstance(getContext());

        if (getArguments() != null) {
            mColumnCount = getArguments().getInt(ARG_COLUMN_COUNT);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_tutor_list, container, false);

        // Set the adapter
        if (view instanceof RecyclerView) {
            Context context = view.getContext();
            RecyclerView recyclerView = (RecyclerView) view;
            if (mColumnCount <= 1) {
                recyclerView.setLayoutManager(new LinearLayoutManager(context));
            } else {
                recyclerView.setLayoutManager(new GridLayoutManager(context, mColumnCount));
            }

            refreshTutorList(recyclerView);

        }
        return view;
    }

    private void refreshTutorList(final RecyclerView recyclerView) {
        Call<List<Tutor>> tutorList = apiBackend.apiService.getAvailableTutors();
        tutorList.enqueue(new Callback<List<Tutor>>() {
            @Override
            public void onResponse(Call<List<Tutor>> call, Response<List<Tutor>> response) {
                recyclerView.setAdapter(new SearchTutorRecyclerViewAdapter(response.body(), mListener));
            }

            @Override
            public void onFailure(Call<List<Tutor>> call, Throwable t) {
                Toast toast = Toast.makeText(getContext(), "There was a network error searching for tutors! Try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }


    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnSearchTutorFragmentInteractionListener) {
            mListener = (OnSearchTutorFragmentInteractionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnMyTutorsFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p/>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnSearchTutorFragmentInteractionListener {
        // TODO: Update argument type and name
        void onSearchTutorsFragmentInteraction(Tutor item);
    }

}
